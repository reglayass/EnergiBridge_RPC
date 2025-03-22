import argparse

from rpc_measure import energibridge_rpc

EXP = "nonservice"
PORT = 8095

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp", "-e", type=str, default="nonservice", help="EnergiBridgerun-method [DEFAULT: nonservice]")
    parser.add_argument("--port", "-p", type=int, help="Port number for RPC [Default: 8095]")
    parser.add_argument("--number", "-n", type=int, default=5, help="Fibonacci number to calculate [Default: 5]")
    
    args = parser.parse_args()
    exp = args.exp or EXP
    port = args.port or PORT
    num = args.number

    @energibridge_rpc(port, exp)
    def fib(n: int = 1) -> int:
        return 1 if n == 0 or n == 1 else fib(n - 1) + fib(n - 2)


    print(fib(num))
