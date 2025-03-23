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


def start_rust():
    print("\t\tStarting Rust server...")
    server_proc = subprocess.Popen(["cargo", "run", "--release", "--", "-u"], cwd=ROOT / "rust_svc",
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   env={**os.environ, "RUSTFLAGS": "-Awarnings"})

    started = False
    # check if its still building
    while not started:
        line = server_proc.stdout.readline()
        print(line)
        if "Energibridge RPC server running on port" in line:
            started = True
        if server_proc.poll() is not None:
            raise RuntimeError("Failed to start Rust server")
    print("\t\tRust server started.")
    return server_proc


def start_cpp():
    print("\t\tStarting C++ server...")
    server_proc = subprocess.Popen(["./server"], cwd=ROOT / "cpp", stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("\t\tCppserver started.")

    return server_proc


def run_experiment(exp, port, num):
    args = ["python", "test.py", f"--exp={exp}", f"--num={num}"]
    if port:
        args.append(f"--port={port}")

    # ignore output
    proc = subprocess.run(args, cwd=ROOT / "py", stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    if "ERROR" in proc.stdout or "Error" in proc.stdout:
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
            server = None

            print(f"\tIteration {i}: running {exp} with n={n}...")
            if exp == "rust":
                server = start_rust()
            elif exp == "cpp":
                server = start_cpp()

            if server:
                print("\t\tCooling down from server start for 5 seconds...")
                sleep(5)

            run_experiment(exp, port_map[exp], n)

            # Stop server
            print("\t\tFib function done")
            if server:
                print("\t\tStopping server...")
                server.terminate()
                server.wait()
                print("\t\tServer stopped.")

            # Reads latest csv file, TODO setup dir for classic energibridge
            current_result = pd.read_csv(
                max(glob.glob(os.path.join(ROOT / "py", "energy_results", "*.csv")), key=os.path.getctime))
            if n not in results:
                results[n] = {}
            if exp not in results[n]:
                results[n][exp] = []
            results[n][exp].append(current_result)

            print(current_result)

            print("\t\tSleep for 30 seconds...")
            sleep(30 if prod else 1)


    print("Experiment finished.")

    # TODO process results
