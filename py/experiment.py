import ctypes
import glob
import itertools
import os
import subprocess
import sys
from pathlib import Path
from time import sleep

import pandas as pd

ROOT = Path(__file__).parent.parent
port_map = {
    "cpp": 8383,
    "rust": 8095,
    "nonservice": None,
}


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def start_rust(server_proc: subprocess.Popen):
    print("\t\tStarting Rust server...")
    server_proc.stdout.flush()
    server_proc.stdin.write(f"cd {ROOT / 'rust_svc'}\n")
    background_proc.stdin.flush()
    server_proc.stdin.write("RUSTFLAGS=\"-A warnings\" cargo run -q --release -- -u &\n")
    background_proc.stdin.flush()
    started = False
    # check if its still building
    while not started:
        line = server_proc.stdout.readline()
        if "Energibridge RPC server running on port" in line:
            started = True
        if server_proc.poll() is not None:
            raise RuntimeError("Failed to start Rust server")
    print("\t\tRust server started.")
    print("\t\tCooling down from server start for 5 seconds...")
    sleep(5)


def start_cpp(server_proc: subprocess.Popen):
    print("\t\tStarting C++ server...")
    server_proc.stdin.write(f"cd {ROOT / 'cpp'}")

    server_proc.stdin.write("TO ADD &\n")
    background_proc.stdin.flush()
    print("\t\tCooling down from server start for 5 seconds...")
    sleep(5)


def run_experiment(exp, port, num):
    args = ["python", "test.py", f"--exp={exp}", f"--num={num}"]
    if port:
        args.append(f"--port={port}")

    # ignore output
    proc = subprocess.run(args, cwd=ROOT / "py", stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    if "ERROR" in proc.stdout:
        raise RuntimeError(f"Error while running experiment: {proc.stdout}")
    else:
        print(f"\t\tResult: {proc.stdout}")


if __name__ == "__main__":
    prod = False  # TODO remove this or change to True when running on production
    iterations = 3
    results = {}

    if sys.platform == "win32" and not is_admin():
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

    background_proc = subprocess.Popen(["bash"] if sys.platform != "win32" else ["powershell"], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=5)
    if sys.platform == "win32":
        # TODO what if RAPL was not initialized?
        background_proc.stdin.write("sc start rapl\n")
        background_proc.stdin.flush()

    # Warm up
    print("Warming up...")
    run_experiment("nonservice", None, 30)
    print("Warm up done.")
    print("Sleep for 30 seconds...")
    sleep(30 if prod else 1)

    instances = ["rust", "cpp", "nonservice"]
    fib_ns = [5, 35]
    experiments = list(itertools.product(instances, fib_ns))

    print("Starting experiments...")
    for i in range(iterations):
        for (exp, n) in experiments:

            print(f"\tIteration {i}: running {exp} with n={n}...")
            if exp == "rust":
                start_rust(background_proc)
            elif exp == "cpp":
                start_cpp(background_proc)

            # TODO classic energibridge, feel free to use background_proc , rapl is already enabled
            run_experiment(exp, port_map[exp], n)

            # TODO handle the case where classic energibridge is used, i.e. no server
            # Stop server
            # kill all child process of the shell
            print("\t\tFib function done, stopping server...")
            background_proc.stdin.write(
                "Stop-Process -Id (" +
                "Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $PID })" +
                ".ProcessId -Force\n" if sys.platform == "win32" else "pkill -P $$\n")
            print("\t\tServer stopped.")

            # Reads latest csv file, TODO setup dir for classic energibridge
            current_result = pd.read_csv(
                max(glob.glob(os.path.join(ROOT / "py", "energy_results", "*.csv")), key=os.path.getctime))
            if n not in results:
                results[n] = {}
            if exp not in results[n]:
                results[n][exp] = []
            results[n][exp].append(current_result)

            # print(current_result)

            print("\t\tSleep for 30 seconds...")
            sleep(30 if prod else 1)

    if sys.platform == "win32":
        background_proc.stdin.write("sc stop rapl\n")
        background_proc.stdin.flush()
    background_proc.terminate()

    print("Experiment finished.")

    # TODO process results
