#include <iostream>

#include "gen/abstractstubserver.h"
#include <jsonrpccpp/server/connectors/httpserver.h>
#include <jsonrpccpp/common/exception.h>
#include <stdio.h>

#include <cstdlib>
#include <sstream>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>

#ifdef _WIN32
    #include <windows.h>
    #define PROCESS_TYPE HANDLE
#else
    #include <unistd.h>
    #include <sys/types.h>
    #include <csignal>
    #define PROCESS_TYPE pid_t
#endif

using namespace jsonrpc;

class EnergiBridge_RPC : public AbstractStubServer {
public:
    EnergiBridge_RPC(AbstractServerConnector &connector, serverVersion_t type);

    virtual bool start_measurements(const std::string& function_name);
    virtual Json::Value stop_measurements(const std::string& function_name);

private:
    PROCESS_TYPE process_handle = -1; // Process of Energibridge
};

EnergiBridge_RPC::EnergiBridge_RPC(AbstractServerConnector &connector, serverVersion_t type) : AbstractStubServer(connector, type) {}

bool is_energibridge_running() {
    return system("pgrep energibridge > /dev/null");
}

bool EnergiBridge_RPC::start_measurements(const std::string &function_name) {
    // if (is_energibridge_running()) {
        // throw JsonRpcException(-32001, "There is already a measurement running!");
    // }

    std::cout << "Starting measurement: " << function_name << std::endl;

    char results_filename[50];
    #ifdef _WIN32
        sprintf_s(results_filename, "results_%s.csv", function_name.c_str());
    #else
        sprintf(results_filename, "results_%s.csv", function_name.c_str());
    #endif;

    char output[100];
    #ifdef _WIN32
        sprintf_s(output, "--output=%s", results_filename);
    #else
        sprintf(output, "--output=%s", results_filename);
    #endif

    #ifdef _WIN32
        std::string command = "energibridge.exe " + std::string(output) + " sleep infinity";

        STARTUPINFOA si;
        PROCESS_INFORMATION pi;
        ZeroMemory(&si, sizeof(si));
        si.cb = sizeof(si);
        ZeroMemory(&pi, sizeof(pi));

        if (CreateProcessA(
                NULL,                      // Application name
                &command[0],               // Command line
                NULL, NULL,                // Process handle not inheritable
                FALSE,                     // Set handle inheritance to FALSE
                0,                         // No special flags
                NULL,                      // Use parent's environment block
                NULL,                      // Use parent's starting directory 
                &si,                       // Pointer to STARTUPINFO structure
                &pi                        // Pointer to PROCESS_INFORMATION structure
            )) 
        {
            CloseHandle(pi.hThread);  // Close thread handle
            process_handle = pi.hProcess; // Store process handle
            std::cout << "Started process with handle: " << process_handle << std::endl;
            return true;
        } else {
            throw JsonRpcException(-32001, "Failed to start the process!");
        }
    #else
        // Fork the process
        process_handle = fork();
        if (process_handle == 0) {
            // Child process: Replace with your command
            execlp("./energibridge", "energibridge", output, "sleep", "infinity", (char *)NULL);
            exit(1);  // If exec fails
        } else if (process_handle > 0) {
            std::cout << "Started process with PID: " << process_handle << std::endl;
            return true;
        } else {
            throw JsonRpcException(-32001, "Failed to start the process!");
        }
    #endif

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

Json::Value EnergiBridge_RPC::stop_measurements(const std::string& function_name) {
    Json::Value response(Json::arrayValue);


    #ifdef _WIN32:
        if (process_handle) {
            std::cout << "Stopping measurement: " << function_name << std::endl;

            if (TerminateProcess(process_handle, 0)) {
                std::cout << "Process terminated." << std::endl;
                CloseHandle(process_handle);
                process_handle = NULL;

                // Read the results CSV file
                char results_filename[50];
                sprintf_s(results_filename, "results_%s.csv", function_name.c_str());

                return read_csv(results_filename);
            } else {
                throw JsonRpcException(-32001, "Failed to terminate process!");
            }
        } else {
            throw JsonRpcException(-32001, "No process running!");
        }
    #else
        if (process_handle > 0) {
            std::cout << "Stopping measurement: " << function_name << " (PID: " << process_handle << ")" << std::endl;
            if (kill(process_handle, SIGTERM) == 0) {
                std::cout << "Process terminated." << std::endl;
                process_handle = -1;  // Reset PID

                // Read the results CSV file
                // convert to JSON array of objects
                const char* func = function_name.c_str();
                char results_filename[50];
                sprintf(results_filename, "results_%s.csv", func);

                return read_csv(results_filename);
            } else {
                throw JsonRpcException(-32001, "Failed to terminate process!");
            }
        } else {
            throw JsonRpcException(-32001, "No process running!");
        }
    #endif

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