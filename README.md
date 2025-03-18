# EnergiBridge As A Service

## Cloning the Repository

## C++ Version

### Requirements
Before running the server, make sure you follow the instructions [here](https://github.com/cinemast/libjson-rpc-cpp?tab=readme-ov-file#install-the-framework) to install the necessary packages.

This version requires you to have `cmake` installed. The following three lines will compile the RPC server and create an executable under `build/bin/EnergiBridge_RPC`

```
cd cpp/build
cmake ..
make
```

Now you can run the server like so:

```
sudo ./build/bin/EnergiBridge_RPC
```

## Typescript Version
You need to install a couple of packages before running.
```
cd /ts
npm install
```
To start the server run `npx ts-node server.ts`. To run the client, execute in a separate terminal `npx ts-node client.ts`.