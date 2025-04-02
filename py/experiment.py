import ctypes
import glob
import itertools
import os
import pickle
import random
import subprocess
from datetime import datetime
from pathlib import Path
from time import sleep
import argparse

import pandas as pd
import requests
from jsonrpcclient import request_uuid, parse

ROOT = Path(__file__).parent.parent
port_map = {
    "cpp": 8383,
    "rust": 8095,
    "nonservice": None,
}

PID = os.getpid()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def start_rust():
    print("\t\tStarting Rust server...")
    server_proc = subprocess.Popen(["./energibridge", "-u"], cwd=ROOT / "py",
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

def run_experiment_sleep(exp, num):
    args = ["sleep", str(num)]
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if exp == "nonservice":
        subprocess.run(["./energibridge",
                        f"--output=./energy_results/{exp}_sleep{num}_{now}.csv",
                        *args], cwd=ROOT / "py")
        return

    ## Send start_measurement
    params = {"pid": PID, "function_name": f"sleep_{num}"}
    requests.post(f"http://localhost:{port_map[exp]}/", json=request_uuid("start_measurements", params))

    # Allow time for server to setup energibridge
    sleep(1)
    subprocess.run(args)
    response = requests.post(f"http://localhost:{port_map[exp]}/", json=request_uuid("stop_measurements", params))
    res = parse(response.json())
    pd.DataFrame(res.result).to_csv(ROOT / "py" / "energy_results"/ f"{exp}_sleep{num}_{now}.csv", header=True, index=False)


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
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--iterations', default=30, help="Number of iterations of the experiment to run. Defaults to 30.", type=int)
    parser.add_argument('-p', '--production', action='store_true')
    
    args = parser.parse_args()
    
    prod = args.production
    iterations = args.iterations
    results = {}

    build_servers()

    # Warm up
    print("Warming up...")
    run_experiment("nonservice", None, 30)
    print("Warm up done.")
    print("Sleep for 30 seconds...")
    sleep(30 if args.production else 1)
    
    instances = ["rust", "cpp", "nonservice"]
    experiments = []

    fib_ns = [10, 35, 40]
    experiments_fib = list(itertools.product(instances,["fib"], [10, 35, 40]))
    experiments.extend(experiments_fib)
    sleep_s = [10,20]
    experiments_sleep = list(itertools.product(instances,["sleep"], [10,20]))
    experiments.extend(experiments_sleep)

    print("Starting experiments...")
    for i in range(iterations):
        for (exp, func, n) in experiments:
            server = None

            print(f"\tIteration {i}: running {exp} for {func} with n={n}...")
            if exp == "rust":
                server = start_rust()
            elif exp == "cpp":
                server = start_cpp()

            if server:
                print("\t\tCooling down from server start for 5 seconds...")
                sleep(5)
            print(f"\t\tRunning {func} with n={n}...")

            if func == "fib":
                run_experiment(exp, port_map[exp], n)
            elif func == "sleep":
                run_experiment_sleep(exp, n)

            # Stop server
            print(f"\t\tRunning {func} with n={n} done")
            if server:
                print("\t\tStopping server...")
                server.terminate()
                server.wait()
                print("\t\tServer stopped.")

            # Reads latest csv file
            latest_csv = max(glob.glob(os.path.join(ROOT / "py", "energy_results", "*.csv")), key=os.path.getctime)
            current_result = pd.read_csv(latest_csv)
            if func not in results:
                results[func] = {}
            if n not in results[func]:
                results[func][n] = {}
            if exp not in results[func][n]:
                results[func][n][exp] = []
            results[func][n][exp].append(current_result)
            os.remove(latest_csv)
            # print(current_result)

            print("\t\tSleep for 30 seconds...")
            sleep(30 if prod else 1)
        random.shuffle(experiments)

    print("Experiment finished.")

    # Its important to use binary mode
    file = open(ROOT / 'py' / "results.pkl", 'wb')

    # source, destination
    pickle.dump(results, file)
    file.close()

    os.remove(ROOT / "py" / "energibridge")
    os.remove(ROOT / "py" / "EnergiBridge_CPP_RPC")

    # TODO process results
    ## EXAMPLE use case
    file = open(ROOT/'py'/ "results.pkl", 'rb')
    results = pickle.load(file)
    print(results)
    file.close()

