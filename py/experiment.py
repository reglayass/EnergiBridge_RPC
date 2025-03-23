import ctypes
import glob
import itertools
import os
import pickle
import subprocess
from datetime import datetime
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
    server_proc = subprocess.Popen(["./energibridge", "-u", "-i=50"], cwd=ROOT / "py",
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return server_proc


def start_cpp():
    print("\t\tStarting C++ server...")
    server_proc = subprocess.Popen(["./EnergiBridge_CPP_RPC"], cwd=ROOT / "py", stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("\t\tCpp server started.")

    return server_proc


def run_experiment(exp, port, num):
    args = ["python", "test.py", f"--exp={exp}", f"--num={num}"]

    if exp == "nonservice":
        subprocess.run(["./energibridge",
                        f"--output=./energy_results/{exp}_fib_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv",
                        *args], cwd=ROOT / "py")
        return

    if port:
        args.append(f"--port={port}")

    # ignore output
    proc = subprocess.run(args, cwd=ROOT / "py", stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    if "ERROR" in proc.stdout or "Error" in proc.stdout:
        raise RuntimeError(f"Error while running experiment: {proc.stdout}")
    else:
        print(f"\t\tResult: {proc.stdout}")


def build_servers():
    # Note this only works for UNIX based OS
    print("Building energibridge...")
    subprocess.run(["cargo", "build", "-r", "-q"], cwd=ROOT / "rust_svc", env={**os.environ, "RUSTFLAGS": "-Awarnings"})
    subprocess.run(
        ["mv", f"{ROOT / 'rust_svc' / 'target' / 'release' / 'energibridge'}", f"{ROOT / 'py' / 'energibridge'}"])

    print("Building CPP energibridge server ...")
    subprocess.run(["cmake", ".."], cwd=ROOT / "cpp" / "build")
    subprocess.run(["make"], cwd=ROOT / "cpp" / "build")
    subprocess.run(
        ["mv", f"{ROOT / 'cpp' / 'build' / 'bin' / 'EnergiBridge_RPC'}", f"{ROOT / 'py' / 'EnergiBridge_CPP_RPC'}"])


if __name__ == "__main__":
    prod = False  # TODO remove this or change to True when running on production
    iterations = 1 # TODO change this as appropriate
    results = {}

    build_servers()

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

            # Reads latest csv file
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

    print("Experiment finished.")

    # Its important to use binary mode
    file = open(ROOT / 'py' / 'results.pkl', 'ab')

    # source, destination
    pickle.dump(results, file)
    file.close()

    os.remove(ROOT / "py" / "energibridge")
    os.remove(ROOT / "py" / "EnergiBridge_CPP_RPC")

    # TODO process results
    ## EXAMPLE use case
    file = open(ROOT/'py'/'results.pkl', 'rb')
    results = pickle.load(file) ## This will be a dict of dict of list of dataframes i.e each df = 1 iteration
    print(results)
    file.close()

