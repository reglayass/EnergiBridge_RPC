# EnergiBridge As A Service

## Cloning the Repository

Clone the repository like so:

```
git clone --recurse-submodules https://github.com/reglayass/EnergiBridge_RPC
```

If you've already cloned but without the `--recurse-submodules` flag, run these two lines:

```
git submodule init
git submodule update
```

## C++ Version

### Requirements
This version requires you to have `cmake` installed. The following three lines will compile the RPC server and create an executable under `build/bin/CEnergiBridge`

```
cd cpp/build
cmake ..
make
```

Now you can run the server like so:

```
./build/bin/EnergiBridge
```