import asyncio
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from rpc_measure import decorator
from rpc_measure.decorator import energibridge_rpc, send_rpc_request


def test_configure_rpc():
    custom_url = "http://custom_url"
    decorator.configure_rpc(custom_url, Path("custom_dir"))
    assert decorator.RPC_URL == custom_url
    assert decorator.OUTPUT_PATH == Path("custom_dir")


@patch("rpc_measure.decorator.requests.post")
def test_send_rpc_request_success(mock_post):
    expected_result = [{"duration": 123, "function": "test_func"}]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"jsonrpc": "2.0", "result": expected_result, "id": 123}
    mock_post.return_value = mock_response

    result = send_rpc_request("dummy_method", {"key": "value"})
    assert result == expected_result
    mock_post.assert_called_once()


@patch("rpc_measure.decorator.requests.post")
def test_send_rpc_request_error_response(mock_post):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "error": {
            "code": -32600,
            "message": "Invalid Request",
            "data": None,
        },
        "id": 123
    }

    mock_post.return_value = mock_response

    with pytest.raises(RuntimeError, match="Energibridge RPC error: Invalid Request"):
        send_rpc_request("dummy_method", {})


@patch("rpc_measure.decorator.requests.post")
def test_rpc_measure_sync_function(mock_post):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = [
        {"jsonrpc": "2.0", "result": None, "id": 123},  # start_measure
        {
            "jsonrpc": "2.0",
            "result": [{"duration": 5, "function": "sync_func"}],
            "id": 123,
        },  # stop_measure
    ]
    mock_post.return_value = mock_response

    @energibridge_rpc(port=1234)
    def sync_func(x):
        return x + 1

    result = sync_func(1)
    assert result == 2
    assert decorator.PORT == 1234
    assert decorator.PID == os.getpid()


@patch("rpc_measure.decorator.requests.post")
@pytest.mark.asyncio
async def test_rpc_measure_async_function(mock_post):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = [
        {"jsonrpc": "2.0", "result": None, "id": 123},  # start_measure
        {
            "jsonrpc": "2.0",
            "result": [{"duration": 10, "function": "async_func"}],
            "id": 123,
        },  # stop_measure
    ]
    mock_post.return_value = mock_response

    @energibridge_rpc()
    async def async_func(x):
        await asyncio.sleep(0.01)
        return x * 2

    result = await async_func(3)
    assert result == 6
