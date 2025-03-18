#include <iostream>

#include "gen/abstractstubserver.h"
#include <jsonrpccpp/server/connectors/httpserver.h>
#include <stdio.h>

#include <cstdlib>
#include <csignal>
#include <unistd.h>
#include <sstream>
#include <cstdio>
#include <cstring>
#include <sys/wait.h>

using namespace jsonrpc;

class EnergiBridge_RPC : public AbstractStubServer {
public:
    EnergiBridge_RPC(AbstractServerConnector &connector, serverVersion_t type);

    virtual bool start_measure(const std::string& function_name);
    virtual bool stop_measure(const std::string& function_name);

private:
    pid_t process_pid = -1; // Process of Energibridge
};

EnergiBridge_RPC::EnergiBridge_RPC(AbstractServerConnector &connector, serverVersion_t type) : AbstractStubServer(connector, type) {}

bool EnergiBridge_RPC::start_measure(const std::string &function_name) {
    std::cout << "Starting measurement: " << function_name << std::endl;

    // Fork the process
    process_pid = fork();
    if (process_pid == 0) {
        // Child process: Replace with your command
        execlp("./energibridge", "energibridge", "--output=results.csv", "sleep", "infinity", (char *)NULL);
        exit(1);  // If exec fails
    } else if (process_pid > 0) {
        std::cout << "Started process with PID: " << process_pid << std::endl;
        return true;
    } else {
        std::cerr << "Failed to start process!" << std::endl;
        return false;
    }

    return false;
}

bool EnergiBridge_RPC::stop_measure(const std::string& function_name) {
    if (process_pid > 0) {
        std::cout << "Stopping measurement: " << function_name << " (PID: " << process_pid << ")" << std::endl;
        if (kill(process_pid, SIGTERM) == 0) {
            std::cout << "Process terminated." << std::endl;
            process_pid = -1;  // Reset PID
            return true;
        } else {
            std::cerr << "Failed to terminate process!" << std::endl;
            return false;
        }
    } else {
        std::cerr << "No process running!" << std::endl;
        return false;
    }

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