project(CEnergiBridge)

cmake_minimum_required(VERSION 3.22)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory(external/rpclib)

add_executable(CEnergiBridge main.cpp)
target_link_libraries(CEnergiBridge PRIVATE rpc)
target_include_directories(CEnergiBridge PRIVATE ${rpclib_INCLUDE_DIRS})

set_target_properties(CEnergiBridge PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)