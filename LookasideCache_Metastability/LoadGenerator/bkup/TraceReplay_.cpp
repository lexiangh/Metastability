// TraceReplay.cpp - Trace replay client code.
//
// Copyright (c) 2018 Timothy Zhu.
// Licensed under the MIT License. See LICENSE file for details.
//

#include <stdint.h>
#include <errno.h>
#include <unistd.h>
#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <cstdlib>
#include "curl/curl.h"
#include "TraceReader.hpp"
#include "time.hpp"
#define EXPERIMENT_TIME 1
using namespace std;
string ngnix_server_ip = "10.158.34.171";
BaseTraceReader* traceReader = NULL;
//string baseUrl = "http://localhost/";
string baseUrl = "http://" + ngnix_server_ip + "/index.php";
bool openLoop = true;
string resultsFilename = "results";
int numThreads = 8;
uint64_t traceStartTime;
uint64_t _experiment_end_time;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
vector<uint64_t> responseTimes;

size_t writefunc(void *ptr, size_t size, size_t nmemb, std::string *s) 
{
  s->append(static_cast<char *>(ptr), size*nmemb);
  return size*nmemb;
}

class TraceReplay {
public:
    virtual ~TraceReplay() {}
    virtual void Replay(const TraceEntry& entry) = 0;
};

class WebTraceReplay : public TraceReplay {
private:
    CURL* curl;

public:
    WebTraceReplay() {
        curl = curl_easy_init();
        curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1); // Fix curl bug with signals
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writefunc);
        curl_easy_setopt(curl, CURLOPT_VERBOSE, 1);
    }
    virtual ~WebTraceReplay() {
        curl_easy_cleanup(curl);
    }

    void AddParam(string& url, const TraceEntry& entry){
        url = url + "?";
        url = url + "request_type=" + entry.requestType
                  + "\\&request_size=" + to_string(entry.requestSize) 
                  + "\\&arrival_time="+ to_string(entry.arrivalTime) + 
                  + "\\&retry_policy=" + to_string(0); 

    }

    virtual void Replay(const TraceEntry& entry) {
        // Set URL
        string response;
        string url = baseUrl ; //+ entry.requestType;
        AddParam(url, entry); //to be refactored
        
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        // Execute request
        CURLcode res = curl_easy_perform(curl);
        // print error
         if(res != CURLE_OK)
                fprintf(stderr, "curl_easy_perform() failed: %sn",
            curl_easy_strerror(res));

        cout<<"curl response: " << response<<endl;

    }
};

TraceReplay* CreateTraceReplay()
{
    return new WebTraceReplay();
}

void* WorkerThread(void* ptr)
{
   // cout<<"WorkerThread Executed"<<endl;
    TraceReplay* replay = CreateTraceReplay();
    // Sleep until start time
    //cout<<"before sleep"<<endl;
    // uint64_t before_sleep = GetTime();
    AbsoluteSleepUninterruptible(traceStartTime);
     //uint64_t after_sleep = GetTime();
    //cout<<"after sleep"<<endl;
    //cout<<"slept for: "<<  (after_sleep - before_sleep)/ NS_PER_SEC<<" seconds"<<endl;

    TraceEntry entry;
    while (traceReader->nextEntry(entry)) {
        // Open loop sleeps until arrival time
        // Closed loop just executes requests as soon as possible
        uint64_t startTime;
        if (openLoop) {
            uint64_t arrivalTime = entry.arrivalTime + traceStartTime;
            AbsoluteSleepUninterruptible(arrivalTime);
            startTime = arrivalTime;
           
            /* shouldn't we progress the traceStartTime as new arrivals come? 

            traceStartTime = arrivalTime;
           
            if(arrivalTime > _experiment_end_time){
                cout<<"time exhausted"<<endl;
                break;
            }
            */

        } else {
            startTime = GetTime();            
        }
        // Replay request
        replay->Replay(entry);
        traceReader->increment_request_counter();
        // Record response time
        uint64_t endTime = GetTime();
        uint64_t responseTime = endTime - startTime;
        cout<<"response time: "<< responseTime/NS_PER_SEC<<" seconds"<<endl;
        pthread_mutex_lock(&mutex);
        responseTimes.push_back(responseTime);
        pthread_mutex_unlock(&mutex);
    }
    delete replay;
    return NULL;
}

void usage(char* argv0)
{
    cerr << "Usage: " << argv0 << " -t traceFile [-r resultsFilename] [-u baseUrl] [-n numThreads] [-o] [-c]" << endl;
    exit(-1);
}

int main(int argc, char** argv)
{
    // Process command line options
    int opt = 0;
    string filename;
    do {
        cout<<"options loop"<<endl;
        opt = getopt(argc, argv, "t:r:u:n:oc");
        cout<<"option = " << opt <<endl;
        switch (opt) {
            case 't':
                filename.assign(optarg);
                break;

            case 'r':
                resultsFilename.assign(optarg);
                break;

            case 'u':
                baseUrl.assign(optarg);
                break;

            case 'n':
                numThreads = atoi(optarg);
                break;

            case 'o':
                openLoop = true;
                break;

            case 'c':
                openLoop = false;
                break;

            case -1:
                break;

            default:
                usage(argv[0]);
                break;
        }
    } while (opt != -1);


    traceStartTime = GetTime() + ConvertSecondsToTime(5);
    _experiment_end_time = traceStartTime + EXPERIMENT_TIME * NS_PER_SEC; 
    // Create trace and check arguments
    traceReader = new TraceReader(traceStartTime);
    if ((traceReader == NULL) || (numThreads < 1)) {
        usage(argv[0]);
    }
    
    cout<<"Number of threads: "<< numThreads<<endl;

    // Allow 5 seconds for warm up and initialization
   
    // Create worker threads
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);
    pthread_t* threadArray = new pthread_t[numThreads];
    if (threadArray == NULL) {
        cerr << "Failed to create thread array" << endl;
        exit(1);
    }
    for (int i = 0; i < numThreads; i++) {
        int rc = pthread_create(&threadArray[i],
                                &attr,
                                WorkerThread,
                                NULL);
        if (rc) {
            cerr << "Error creating thread: " << rc << " errno: " << errno << endl;
            exit(-1);
        }
    }

    // Join all threads
    for (int i = 0; i < numThreads; i++) {
        int rc = pthread_join(threadArray[i], NULL);
        if (rc) {
            cerr << "Error joining thread: " << rc << " errno: " << errno << endl;
            exit(-1);
        }
    }

    
    cout<<"Experiment time exhausted. Total number of requests sent: "<< traceReader->get_request_count()<<endl;
    traceReader->reset_request_counter();
    // Output results
    pthread_mutex_lock(&mutex);
    ofstream resultsFile(resultsFilename.c_str());
    for (unsigned int i = 0; i < responseTimes.size(); i++) {
        resultsFile << responseTimes[i] << endl;
    }
    resultsFile.close();
    pthread_mutex_unlock(&mutex);

    // Cleanup
    pthread_attr_destroy(&attr);
    delete[] threadArray;
    delete traceReader;
    return 0;
}
