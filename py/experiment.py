from pathlib import Path
import os 
from time import sleep
import subprocess

ROOT = Path(__file__).parent.parent
port_map = {
    "cpp": 8383,
    "rust": 8095,
    "nonservice": None,
}
experiments = ["rust", "cpp", "nonservice"]

def start_rust():
    server = subprocess.run(
        ["cargo", "run", "--release", "--", "-u"],
        cwd=ROOT / "rust_svc"
    )
    return server

def start_cpp():
    cpp_proc = subprocess.Popen(
        ["TO ADD"],
        cwd=ROOT / "cpp"
    )
    print("Starting C++ server...")

def run_experiment(exp, port, num):
    os.chdir(ROOT / "py")
    os.system(f"python test.py --exp={exp} --num={num} --port={port}")

if __name__ == "__main__":
    for exp in experiments:
        if exp == "rust":
            server = start_rust()
        elif exp == "cpp":
            server = start_cpp()

        for num in [5, 35]:
            print(f"Running experiment {exp} with Fib({num})")
            for i in range(3):
                print(f"Running experiment {exp} iteration {i + 1}")
                run_experiment(exp, port_map[exp], num)
                print("Sleeping for 30s...")
                sleep(30)

        print(f"Finished experiment {exp}")
        server.terminate()
        print("Sleeping for 15s...")
        sleep(15)
