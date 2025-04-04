# EnergiBridge As A Service
## Disclaimer
The code in this repository have been only tested to work correctly in the following OS:
- macOS Sequoia 15.3.2
- Pop_OS! 22.04

## Cloning the Repository
This repository contains **submodules** for the Rust implementation of the service. To clone, please use the following: 

```bash
git clone --recurse-submodules https://github.com/reglayass/EnergiBridge_RPC.git
```

If the submodule folder `rust_svc` is empty, please use the following the commands: 

```bash
git pull
git submodule update --init --recursive
```

## C++ Version
This version requires you to have `cmake` installed. The following three lines will compile the RPC server and create an executable under `build/bin/EnergiBridge_RPC`

### Requirements
#### Packages
- [jsonrpccpp](https://github.com/cinemast/libjson-rpc-cpp?tab=readme-ov-file#install-the-framework)
- [microhttpd](https://www.gnu.org/software/libmicrohttpd/)
- [jsoncpp](https://github.com/open-source-parsers/jsoncpp)

**Note**: For Macos, there may be an option to install the packages via Homebrew


## Building the Server

```
cd cpp/build
cmake ..
make
```

## Running the server
Now you can run the server like so:

```
./bin/EnergiBridge_RPC
```
This will start the server on `http://localhost:8383`, and terminates when you press `Ctrl+C`.

## Rust Version
The rust version is a fork from the original `energibridge`. To pull the latest files from the original repository, run the following command:

```bash
git pull
git submodule init
git submodule update
```

### Requirements
- [Rust installed](https://www.rust-lang.org/tools/install)

### Running the Server
Go to the `rust_svc` directory and run either from a build or from the codebase.

```bash
cd ./rust_svc
````
#### From Build
1. Build the server.
```bash
cargo build -r
```
2. Run the server from the build (for Unix-based) systems
```bash
chmod +x ./target/release/energibridge
./target/release/energibridge -u
````
#### From Codebase
```bash
cargo run --release -- -u    
```
Both will start the server on `http://localhost:8095`, and terminates when you press `Ctrl+C`.

### Example RPC Calls (body) to the Server
#### start_measurement
<details>
<summary>Request</summary>

```json
{
  "jsonrpc": "2.0",
  "id": 123,
  "method": "start_measurements",
  "params": {
    "pid": 4024,
    "function_name": "test_fn"
  }
}
```
</details>


<details>
<summary>Response</summary>

```json
{
  "jsonrpc": "2.0",
  "id": 123,
  "result": true
}
```
</details>


#### stop_measurement
<details>
<summary>Request</summary>

```json
{
  "jsonrpc": "2.0",
  "id": 123,
  "method": "stop_measurements",
  "params": {
    "pid": 4024,
    "function_name": "test_fn"
  }
}
```
</details>

<details>
<summary>Response</summary>

```json
{
    "jsonrpc": "2.0",
    "id": 123,
    "result": [
        {
            "CPU_USAGE_7": 0.0,
            "CPU_FREQUENCY_0": 3228.0,
            "CPU_USAGE_6": 3.7037036418914795,
            "CPU_TEMP_5": 51.43449401855469,
            "CPU_TEMP_0": 51.70053482055664,
            "CPU_USAGE_4": 3.5714287757873535,
            "TOTAL_MEMORY": 34359738368.0,
            "CPU_TEMP_3": 52.072044372558594,
            "CPU_FREQUENCY_2": 3228.0,
            "CPU_TEMP_2": 48.62870788574219,
            "CPU_FREQUENCY_6": 3228.0,
            "CPU_TEMP_9": 49.721649169921875,
            "USED_SWAP": 0.0,
            "CPU_FREQUENCY_3": 3228.0,
            "CPU_TEMP_1": 51.66541290283203,
            "CPU_FREQUENCY_9": 3228.0,
            "TIME": 1742386864844,
            "CPU_USAGE_8": 0.0,
            "SYSTEM_POWER (Watts)": 7.396881103515625,
            "CPU_USAGE_0": 77.77777862548828,
            "CPU_TEMP_4": 50.413665771484375,
            "CPU_FREQUENCY_1": 3228.0,
            "CPU_FREQUENCY_4": 3228.0,
            "TOTAL_SWAP": 0.0,
            "DELTA": 0,
            "CPU_USAGE_9": 0.0,
            "CPU_FREQUENCY_5": 3228.0,
            "CPU_TEMP_8": 50.172760009765625,
            "CPU_USAGE_1": 76.92308044433594,
            "CPU_USAGE_3": 14.814814567565918,
            "CPU_USAGE_2": 3.7037036418914795,
            "CPU_FREQUENCY_8": 3228.0,
            "CPU_FREQUENCY_7": 3228.0,
            "USED_MEMORY": 24933580800.0,
            "CPU_TEMP_7": 47.576141357421875,
            "CPU_USAGE_5": 0.0,
            "CPU_TEMP_6": 49.87007141113281
        },
        ...
    ]
}
```
</details>


# Experiments
We provided a script to run the experiments which writes a pickle file for the results at `./py/experiments.py`

Please ensure all necessary dependencies and/or build tools are installed beforehand (see above).

In order to run the experiments, make sure all dependencies are installed and run the following command:

```
python experiment.py --production
```

If you want to run the experiment for less than 30 iterations, you can specify the amount of iterations using `--iterations={number of iterations to run}`.
