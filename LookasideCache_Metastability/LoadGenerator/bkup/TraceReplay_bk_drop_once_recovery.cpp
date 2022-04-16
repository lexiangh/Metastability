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
#include <sstream>

using namespace std;
string ngnix_server_ip = "10.158.4.21";
string baseUrl = "http://" + ngnix_server_ip + "/index.php";

BaseTraceReader* traceReader = NULL; 
bool openLoop = true;
string resultsFilename = "results";
int numThreads = 8;
uint64_t traceStartTime;

uint64_t drop_start_time;
uint64_t drop_end_time;

int total_hits = 0;
int num_error_responses = 0;
int killed_at_trace_replay = 0; 
int dropped_requests = 0;
int error_responses[1000];
int total_database_hits = 0;


pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

struct request_info{
    uint64_t request_start_time;
    uint64_t response_time;
    uint64_t hit; 
    uint64_t error;
};

vector<request_info> requestInfos;

size_t WriteFunction(void *ptr, size_t size, size_t nmemb, std::string *s) 
{
  s->append(static_cast<char *>(ptr), size*nmemb);
  return size*nmemb;
}

class TraceReplay {
public:
    virtual ~TraceReplay() {}
    virtual int Replay(const TraceEntry& entry) = 0;
};

class WebTraceReplay : public TraceReplay {
private:
    CURL* curl;

public:
    WebTraceReplay() {
        curl = curl_easy_init();
        curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1); // Fix curl bug with signals
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteFunction);
        //curl_easy_setopt(curl, CURLOPT_VERBOSE, 1);
    }
    virtual ~WebTraceReplay() {
        curl_easy_cleanup(curl);
    }


    void AddParam(string& url, const TraceEntry& entry){
            url = url + "?";
            url = url + "request_type=" + entry.requestType
                    + "&request_size=" + to_string(entry.requestSize) 
                    + "&arrival_time="+ to_string(entry.arrivalTime) + 
                    + "&retry_policy=" + to_string(0)
                    + "&request_index=" + to_string(entry.index);

    }

    void process_return_code(int return_code){
        
         pthread_mutex_lock(&mutex);

        if(return_code == 1){
            total_hits++;
        }
        else if(return_code < 0){
            error_responses[ -1 * return_code]++;
            num_error_responses++;
        }
        else if(return_code == 2){
            total_database_hits++;
        }
        else{
            error_responses[ return_code]++;
        }
        

        pthread_mutex_unlock(&mutex);

        /*
        switch (return_code)
        {
            case 1:
                total_hits++;
                break;
            default:
                break;
        }
        */
    }

    virtual int Replay(const TraceEntry& entry) {
        // Set URL
        string response; 
        string url = baseUrl ; //+ entry.requestType;
        AddParam(url, entry); //to be refactored
        //cout<<"request: "<< url<<endl; 
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        // Execute request
        CURLcode res = curl_easy_perform(curl);
        // print error
         if(res != CURLE_OK){
                fprintf(stderr, "curl_easy_perform() failed: %sn",
                curl_easy_strerror(res));
                num_error_responses++;
         }
         //cout<<"response: "<< response<<endl;

     
         std::stringstream ss(response);
         int return_code; 
         ss>>return_code;

        if(response.size() > 4){
            return_code = -99;        
         }
         else if(response.size() == 0){
             return_code = -98;
         }
       //  else{
       //      cout<<"response size: " << response.size()<<endl;
       //  }
         process_return_code(return_code);
         return return_code;
      //  cout<<"curl response: " << response<<endl;
    }
};


TraceReplay* CreateTraceReplay()
{
    return new WebTraceReplay();
}

void* WorkerThread(void* ptr)
{
    TraceReplay* replay = CreateTraceReplay();
    // Sleep until start time
    AbsoluteSleepUninterruptible(traceStartTime);
    TraceEntry entry;
    while (traceReader->nextEntry(entry)) {
        // Open loop sleeps until arrival time
        // Closed loop just executes requests as soon as possible
        uint64_t startTime; 

        if (openLoop) {
            uint64_t arrivalTime = entry.arrivalTime + traceStartTime;

            AbsoluteSleepUninterruptible(arrivalTime);
            startTime = arrivalTime;
            // get current time 
            uint64_t currentTime = GetTime();

            if(currentTime > drop_start_time && currentTime < drop_end_time){                 
                pthread_mutex_lock(&mutex);
                request_info req_info;
                req_info.response_time = currentTime - startTime;
                req_info.request_start_time = startTime;
                req_info.hit = 0;
                req_info.error = 1;
                dropped_requests++;
                requestInfos.push_back(req_info);
                pthread_mutex_unlock(&mutex);
                continue;
            }

            int difference_in_second = (currentTime - startTime)/ (NS_PER_SEC);
            
            if(difference_in_second >= 1){
                
                pthread_mutex_lock(&mutex);
                request_info req_info;
                req_info.response_time = currentTime - startTime;
                req_info.request_start_time = startTime;
                req_info.hit = 0;
                req_info.error = 1;
                killed_at_trace_replay++;
                requestInfos.push_back(req_info);
                pthread_mutex_unlock(&mutex);
            
                continue;
            }

            
        } 
        else {
            startTime = GetTime();
        }


        // Replay request
        int64_t return_code = replay->Replay(entry);
        // Record response time
        uint64_t endTime = GetTime();
        uint64_t responseTime = endTime - startTime;
        pthread_mutex_lock(&mutex);
        request_info req_info;
        req_info.response_time = responseTime;
        req_info.request_start_time = startTime;
        req_info.hit = return_code == 1 ? 1 : 0;
        req_info.error = return_code < 0 ? 1 : 0;
    
        requestInfos.push_back(req_info);
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
        opt = getopt(argc, argv, "t:r:u:n:oc");
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

    // Create trace and check arguments
    traceReader = new TraceReader(filename);
    if ((traceReader == NULL) || (numThreads < 1)) {
        usage(argv[0]);
    }
    // Allow 5 seconds for warm up and initialization
    traceStartTime = GetTime() + ConvertSecondsToTime(5);
    
    drop_start_time = traceStartTime + ConvertSecondsToTime(20);
    drop_end_time = drop_start_time + ConvertSecondsToTime(10);
    //cout<<"sanity test: drop window size = " << (drop_end_time - drop_start_time ) / (NS_PER_SEC * 1.0) <<endl;
    // for a 10 second window... we drop requests (at this point we should already be in metastable state)
    // expectation is that the system recovers 


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
    uint64_t end_time = GetTime();
    uint64_t total_latency = 0;
    double experiment_runtime = ((end_time - traceStartTime) * 1.0) /NS_PER_SEC;
    // Output results
    pthread_mutex_lock(&mutex);
    ofstream resultsFile(resultsFilename.c_str()); 
    // stores differential hits, error responses within each (end - start) times 
    int recalc_total_error = 0;
    resultsFile<<traceStartTime<<endl;
    for (unsigned int i = 0; i < requestInfos.size(); i++) {
        resultsFile << requestInfos[i].request_start_time<< " " << requestInfos[i].response_time << " "
                 <<  requestInfos[i].hit <<" " << requestInfos[i].error << endl; 
        if(requestInfos[i].error == 1){
            recalc_total_error++;
        }
        total_latency+= requestInfos[i].response_time;
    }
    //cout<<"total hits (memcached): "<< total_hits <<endl;
    cout<<"total number of responses: "<< requestInfos.size() <<endl;  
    cout<<"Experiment runtime ="<< experiment_runtime<<endl;
    cout<<"memcached hit rate: "<< ((total_hits* 1.0)/requestInfos.size())<<endl;
    cout<<"approx throughput: "<< requestInfos.size() / experiment_runtime << " requests per second" <<endl; 
    cout<<"average latency: "<< ((total_latency * 1.0)/ NS_PER_SEC) / requestInfos.size() <<endl;
    cout<<"total database hits: "<< total_database_hits << endl;
   // cout<<"total ..not error, not hit rate: "<< both_zeros <<endl;
    cout<<"Total erroneous responses: "<< num_error_responses <<endl;
    cout<<"Killed at trace replay: "<< killed_at_trace_replay<<endl;
    cout<<"Dropped at trace replay: "<< dropped_requests <<endl;

    for(int i=0; i <100; i++){
        if(error_responses[i] != 0){
            cout<<"error_code: "<< i <<" count= "<< error_responses[i]<<endl; 
        }
    }
    
    resultsFile.close();
    pthread_mutex_unlock(&mutex);

    // Cleanup
    pthread_attr_destroy(&attr);
    delete[] threadArray;
    delete traceReader;
    return 0;
}