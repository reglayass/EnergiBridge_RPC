from rpc_measure.decorator import energibridge_rpc, configure_rpc


@energibridge_rpc(enabled=False)
def example_function():
    print("Executing example function...")
    return "Function Completed"

@energibridge_rpc(port=6000)
async def async_example_function():
    print("Executing async example function...")
    await asyncio.sleep(1)
    return "Async Function Completed"

if __name__ == "__main__":
    configure_rpc("http://localhost:6000/jsonrpc")
    print(example_function())
    import asyncio
    asyncio.run(async_example_function())
