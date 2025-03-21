from rpc_measure.decorator import rpc_measure, configure_rpc


@rpc_measure(pid=5678, app_name="ExampleApp")
def example_function():
    print("Executing example function...")
    return "Function Completed"

@rpc_measure(pid=5678, app_name="ExampleApp")
async def async_example_function():
    print("Executing async example function...")
    await asyncio.sleep(1)
    return "Async Function Completed"

if __name__ == "__main__":
    configure_rpc("http://localhost:6000/jsonrpc")
    print(example_function())
    import asyncio
    asyncio.run(async_example_function())
