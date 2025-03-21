import argparse

from rpc_measure import energibridge_rpc

RUN_WITH_RPC = False
PORT = 8095

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rpc", "-r", action="store_true", help="Enable RPC [DEFAULT: False]")
    parser.add_argument("--port", "-p", type=int, help="Port number for RPC [Default: 8095]")
    parser.add_argument("--number", "-n", type=int, default=5, help="Fibonacci number to calculate [Default: 5]")
    args = parser.parse_args()
    RUN_WITH_RPC = args.rpc or RUN_WITH_RPC
    PORT = args.port or PORT
    num = args.number


    @energibridge_rpc(RUN_WITH_RPC, PORT)
    def fib(n: int = 1) -> int:
        return 1 if n == 0 or n == 1 else fib(n - 1) + fib(n - 2)


    print(fib(num))
