# Minimum version of CMake
cmake_minimum_required(VERSION 3.10)

# Project name
project(EnergiBridge_RPC)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)

# Specify the source file
set(SOURCES main.cpp)

# Set output directory for the executable
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Add executable
add_executable(EnergiBridge_RPC ${SOURCES})

# Link libraries
target_link_libraries(EnergiBridge_RPC
    jsoncpp
    microhttpd
    jsonrpccpp-common
    jsonrpccpp-server
)