import asyncio
from unittest.mock import Mock, patch

import pytest

from rpc_measure import decorator
from rpc_measure.decorator import rpc_measure, send_rpc_request


def test_configure_rpc():
    custom_url = "http://localhost:1234/jsonrpc"
    decorator.configure_rpc(custom_url)
    assert decorator.RPC_URL == custom_url


@patch("rpc_measure.decorator.requests.post")
def test_send_rpc_request_success(mock_post):
    expected_result = [{"duration": 123, "function": "test_func"}]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"jsonrpc": "2.0", "result": expected_result}
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
        "error": "some error",
    }
    mock_post.return_value = mock_response

    with pytest.raises(RuntimeError, match="RPC error: some error"):
        send_rpc_request("dummy_method", {})


@patch("rpc_measure.decorator.requests.post")
def test_rpc_measure_sync_function(mock_post):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = [
        {"jsonrpc": "2.0", "result": None},  # start_measure
        {
            "jsonrpc": "2.0",
            "result": [{"duration": 5, "function": "sync_func"}],
        },  # stop_measure
    ]
    mock_post.return_value = mock_response

    @rpc_measure(pid=42, app_name="test_app")
    def sync_func(x):
        return x + 1

    result, dataframe = sync_func(1)
    assert result == 2
    assert not dataframe.empty
    assert dataframe.iloc[0]["function"] == "sync_func"


@patch("rpc_measure.decorator.requests.post")
@pytest.mark.asyncio
async def test_rpc_measure_async_function(mock_post):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = [
        {"jsonrpc": "2.0", "result": None},  # start_measure
        {
            "jsonrpc": "2.0",
            "result": [{"duration": 10, "function": "async_func"}],
        },  # stop_measure
    ]
    mock_post.return_value = mock_response

    @rpc_measure(pid=77, app_name="test_async")
    async def async_func(x):
        await asyncio.sleep(0.01)
        return x * 2

    result, dataframe = await async_func(3)
    assert result == 6
    assert not dataframe.empty
    assert dataframe.iloc[0]["function"] == "async_func"
