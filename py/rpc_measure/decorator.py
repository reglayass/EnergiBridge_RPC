import asyncio
import functools
import uuid
from typing import Any, Callable

import pandas as pd
import requests

RPC_URL = f"http://localhost:5000/jsonrpc"


def configure_rpc(url: str):
    """Configure the RPC URL with a custom port."""
    global RPC_URL
    RPC_URL = url


def send_rpc_request(method: str, params: dict) -> Any:
    """Sends a JSON-RPC request and returns the result."""
    request_id = str(uuid.uuid4())
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id,
    }

    try:
        response = requests.post(RPC_URL, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"RPC request failed: {e}")

    result = response.json()
    if "error" in result:
        raise RuntimeError(f"RPC error: {result['error']}")

    return result.get("result", [])


def rpc_measure(pid: int, app_name: str):
    """Decorator to measure function execution using JSON-RPC."""
    def decorator(func: Callable):
        is_async = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _execute_rpc_measure(func, args, kwargs, pid, app_name)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _execute_rpc_measure_async(func, args, kwargs, pid, app_name)

        return async_wrapper if is_async else sync_wrapper

    return decorator


def _execute_rpc_measure(func: Callable, args: tuple, kwargs: dict, pid: int, app_name: str) -> Any:
    """Handles synchronous function measurement."""
    function_name = func.__name__

    send_rpc_request("start_measure", {"pid": pid, "function_name": function_name})

    result = func(*args, **kwargs)

    response_data = send_rpc_request(
        "stop_measure",
        {"pid": pid, "function_name": function_name, "application_name": app_name}
    )

    dataframe = pd.DataFrame(response_data)
    return result, dataframe


async def _execute_rpc_measure_async(func: Callable, args: tuple, kwargs: dict, pid: int, app_name: str) -> Any:
    """Handles asynchronous function measurement."""
    function_name = func.__name__

    send_rpc_request("start_measure", {"pid": pid, "function_name": function_name})

    result = await func(*args, **kwargs)

    response_data = send_rpc_request(
        "stop_measure",
        {"pid": pid, "function_name": function_name, "application_name": app_name}
    )

    dataframe = pd.DataFrame(response_data)
    return result, dataframe
