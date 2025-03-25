import pickle
from pathlib import Path

ROOT = Path(__file__).parent.parent

file_fib = open(ROOT / 'py' / "results_fib.pkl", 'rb')
results_fib = pickle.load(file_fib)

file_sleep = open(ROOT / 'py' / "results_sleep.pkl", 'rb')
results_sleep = pickle.load(file_sleep)

file = open(ROOT / 'py' / "results.pkl", 'wb')
results_sleep["fib"] = results_fib
pickle.dump(results_sleep, file)

file.close()
file_fib.close()
file_sleep.close()