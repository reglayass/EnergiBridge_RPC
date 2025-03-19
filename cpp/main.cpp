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
#include <fstream>
#include <sstream>
#include <vector>
#include <map>

using namespace jsonrpc;

class EnergiBridge_RPC : public AbstractStubServer {
public:
    EnergiBridge_RPC(AbstractServerConnector &connector, serverVersion_t type);

    virtual bool start_measure(const std::string& function_name);
    virtual Json::Value stop_measure(const std::string& function_name);

private:
    pid_t process_pid = -1; // Process of Energibridge
};

EnergiBridge_RPC::EnergiBridge_RPC(AbstractServerConnector &connector, serverVersion_t type) : AbstractStubServer(connector, type) {}

bool EnergiBridge_RPC::start_measure(const std::string &function_name) {
    std::cout << "Starting measurement: " << function_name << std::endl;

    char results_filename[50];
    sprintf(results_filename, "results_%s.csv", function_name);

    char output[50];
    sprintf(output, "--output=%s", results_filename);

    // Fork the process
    process_pid = fork();
    if (process_pid == 0) {
        // Child process: Replace with your command
        execlp("./energibridge", "energibridge", output, "sleep", "infinity", (char *)NULL);
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

Json::Value read_csv(const char* filename) {
    std::ifstream file(filename);
    Json::Value jsonArray(Json::arrayValue);

    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return jsonArray; // Return empty array on failure
    }

    std::string line;
    std::vector<std::string> headers;

    // Read headers (first line)
    if (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string column;
        while (std::getline(ss, column, ',')) {
            headers.push_back(column);
        }
    }

    // Read data rows
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string cell;
        Json::Value jsonObject;
        size_t colIndex = 0;

        while (std::getline(ss, cell, ',')) {
            if (colIndex < headers.size()) {
                jsonObject[headers[colIndex]] = std::stod(cell);
            }
            colIndex++;
        }

        jsonArray.append(jsonObject);
    }

    file.close();
    std::remove(filename);
    return jsonArray;
}

Json::Value EnergiBridge_RPC::stop_measure(const std::string& function_name) {
    Json::Value response(Json::arrayValue);

    if (process_pid > 0) {
        std::cout << "Stopping measurement: " << function_name << " (PID: " << process_pid << ")" << std::endl;
        if (kill(process_pid, SIGTERM) == 0) {
            std::cout << "Process terminated." << std::endl;
            process_pid = -1;  // Reset PID

            // Read the results CSV file
            // convert to JSON array of objects
            char results_filename[50];
            sprintf(results_filename, "results_%s.csv", function_name);

            return read_csv(results_filename);
        } else {
            std::cerr << "Failed to terminate process!" << std::endl;

            return Json::Value (Json::arrayValue);
        }
    } else {
        std::cerr << "No process running!" << std::endl;
        return Json::Value (Json::arrayValue);
    }

    return Json::Value (Json::arrayValue);
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