#include <iostream>
#include <rpc/server.h>
#include <rpc/this_handler.h>

double divide(double a, double b) {
    if (b == 0) {
        // Error handling
        // Return a tuple with an error code and a message.
        rpc::this_handler().respond_error(
            std::make_tuple(1, "Division by zero.") 
        );
    }
    return a / b; 
}

struct subtractor {
    double operator()(double a, double b) { return a - b; }
};

struct multiplier {
    double multiply(double a, double b) { return a * b; }
};

int main() {
    subtractor s;
    multiplier m;

    // Creates the server
    // Binds on port 8080
    rpc::server srv(8080);

    // Bind the functions in order to expose them
    // Which are the names that the client can use to call the function
    srv.bind("add", [](double a, double b) { return a + b; });
    srv.bind("sub", s);
    srv.bind("div", &divide);
    srv.bind("mul", [&m](double a, double b) { return m.multiply(a, b); });

    // Run the server
    srv.run();

    return 0;
}