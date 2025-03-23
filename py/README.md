# RPC Measure

A Python package to measure function execution using JSON-RPC.

## Installation

Create a virtual environment:
```sh
python -m venv venv
```

Activate the virtual environment:
```sh   
source venv/bin/activate
```

Clone the repository and install dependencies:
```sh
pip install -r requirements.txt
```

Or install via pip as a package:
```sh
pip install .
```

## Usage

### Configuring the RPC URL

```python
from rpc_measure.decorator import configure_rpc
from pathlib import Path

configure_rpc(url="URL", output_path=Path("path/to/file"))
```

### Using the Decorator

```python
from rpc_measure.decorator import energibridge_rpc


@energibridge_rpc(enabled=True, port=1234)
def my_function():
    print("Running...")
    return "Done"


print(my_function())
```
If enabled, the energy measurement will be saved as a csv at the specified output path (`./energy_results/` by default).

## Running Tests

```sh
pytest tests/
```

## Building package
In order to build the package, run the following command:
```sh
python setup.py sdist bdist_wheel
```