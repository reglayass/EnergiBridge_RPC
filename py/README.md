# RPC Measure

A Python package to measure function execution using JSON-RPC.

## Installation

Clone the repository and install dependencies:
```sh
pip install -r requirements.txt
```

Or install via pip:
```sh
pip install .
```

## Usage

### Configuring the RPC URL

```python
from rpc_measure.decorator import configure_rpc

configure_rpc("URL")
```

### Using the Decorator

```python
from rpc_measure.decorator import rpc_measure


@rpc_measure(pid=1234, app_name="MyApp")
def my_function():
    print("Running...")
    return "Done"


print(my_function())
```

## Running Tests

```sh
pytest tests/
```

## Building package
In order to build the package, run the following command:
```sh
python setup.py sdist bdist_wheel
```