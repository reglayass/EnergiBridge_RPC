#include <iostream>
#include <rpc/client.h>

int main () {
    rpc::client c("localhost", 8080);

    std::cout << "add(2, 3) = ";
    double five = c.call("add", 2, 3).as<double>();
    std::cout << five << std::endl;

    return 0;
}