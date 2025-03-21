import asyncio
import functools
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import requests
from jsonrpcclient import request_uuid, parse, Ok

# Default values
RPC_URL: str = "http://localhost"
PID: int = -1
OUTPUT_PATH: Path = Path(__file__).parent.parent / "energy_results"
PORT: int = 8095


def energibridge_rpc(enabled=True, port=8095) -> Callable:
    """Decorator to measure function execution using JSON-RPC."""
    currently_measuring = set()

    def decorator(func: Callable):
        global PID, PORT
        if PID < 0:
            PID = os.getpid()
        PORT = port
        if not OUTPUT_PATH.exists():
            OUTPUT_PATH.mkdir()

        is_async = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if func.__name__ in currently_measuring or not enabled:
                return func(*args, **kwargs)
            currently_measuring.add(func.__name__)
            return _execute_rpc_measure(func, args, kwargs, currently_measuring)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if func.__name__ in currently_measuring or not enabled:
                return await func(*args, **kwargs)
            currently_measuring.add(func.__name__)
            return await _execute_rpc_measure_async(func, args, kwargs, currently_measuring)

        return async_wrapper if is_async else sync_wrapper

    return decorator


def configure_rpc(url: str = RPC_URL, output_path: Path = OUTPUT_PATH) -> None:
    """Configure the RPC URL with a custom value."""
    global RPC_URL, OUTPUT_PATH
    RPC_URL = url
    OUTPUT_PATH = output_path


def _execute_rpc_measure(func: Callable, args: tuple, kwargs: dict, currently_measuring: set) -> Any:
    """Handles synchronous function measurement."""
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    params = {"pid": PID, "function_name": func.__name__}

    try:
        response_data = send_rpc_request("start_measurements", params)
        if response_data is False:
            raise RuntimeError("Failed to start measurement.")
    except Exception as e:
        currently_measuring.remove(func.__name__)
        logging.error(f"Failed to start measurement: {e}")
        return func(*args, **kwargs)

    result = func(*args, **kwargs)
    try:
        response_data = send_rpc_request("stop_measurements", params)
        pd.DataFrame(response_data).to_csv(OUTPUT_PATH / f"{now}_{func.__name__}.csv", header=True, index=False)

    except Exception as e:
        logging.error(f"Failed to stop or collect measurement: {e}")
    finally:
        currently_measuring.remove(func.__name__)

        return result


async def _execute_rpc_measure_async(func: Callable, args: tuple, kwargs: dict, currently_measuring: set) -> Any:
    """Handles asynchronous function measurement."""
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    params = {"pid": PID, "function_name": func.__name__}
    currently_measuring.add(func.__name__)
    try:
        response_data = send_rpc_request("start_measure", params)
        if response_data is False:
            raise RuntimeError("Failed to start measurement.")
    except Exception as e:
        currently_measuring.remove(func.__name__)
        logging.error(f"Failed to start measurement: {e}")
        return await func(*args, **kwargs)

    result = await func(*args, **kwargs)

    try:
        response_data = send_rpc_request("stop_measure", params)
        pd.DataFrame(response_data).to_csv(OUTPUT_PATH / f"{now}_{func.__name__}.csv", header=True, index=False)
    except Exception as e:
        logging.error(f"Failed to stop or collect measurement: {e}")
    finally:
        currently_measuring.remove(func.__name__)
        return result


def send_rpc_request(method: str, params: dict) -> Any:
    """Sends a JSON-RPC request and returns the result."""

    response = requests.post(f"{RPC_URL}:{PORT}/", json=request_uuid(method, params))
    if response.ok is False:
        raise RuntimeError(f"Failed to send RPC request: {response.reason}")
    parsed = parse(response.json())
    if not isinstance(parsed, Ok):
        raise RuntimeError(f"Energibridge RPC error: {parsed.message}")
    return parsed.result
