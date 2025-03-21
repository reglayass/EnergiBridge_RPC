import requests
import json
from time import sleep

def main():
    url = "http://localhost:8383"
    
    payload = {
        "method": "start_measure",
        "params": { "function_name": "funcName" },
        "jsonrpc": "2.0",
        "id": 1
    }
    
    response = requests.post(url, json=payload).json()
    print(response)
    
    sleep(15)
    
    payload = {
        "method": "stop_measure",
        "params": { "function_name": "funcName" },
        "jsonrpc": "2.0",
        "id": 2
    }
    
    response = requests.post(url, json=payload).json()
    print(response)
    
    
if __name__ == "__main__":
    main()