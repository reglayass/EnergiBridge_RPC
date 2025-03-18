#include <iostream>

#include "gen/abstractstubserver.h"
#include <jsonrpccpp/server/connectors/httpserver.h>
#include <stdio.h>

using namespace jsonrpc;

class EnergiBridge_RPC : public AbstractStubServer {
public:
    EnergiBridge_RPC(AbstractServerConnector &connector, serverVersion_t type);

    virtual bool start_measure(const std::string& function_name);
    virtual bool stop_measure(const std::string& function_name);
};

EnergiBridge_RPC::EnergiBridge_RPC(AbstractServerConnector &connector, serverVersion_t type) : AbstractStubServer(connector, type) {}

bool EnergiBridge_RPC::start_measure(const std::string &function_name) {
    std::cout << "Start Measure!" << std::endl;
    return true;
}

bool EnergiBridge_RPC::stop_measure(const std::string& function_name) {
    std::cout << "Stop Measure!" << std::endl;
    return true;
}

int main() {
    HttpServer httpserver(8383);
    EnergiBridge_RPC s(httpserver,
                   JSONRPC_SERVER_V1V2); // hybrid server (json-rpc 1.0 & 2.0)
    s.StartListening();
    std::cout << "Hit enter to stop the server" << std::endl;
    getchar();
  
    s.StopListening();
  
    return 0;
  }