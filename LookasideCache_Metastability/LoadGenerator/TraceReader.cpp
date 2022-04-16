// TraceReader.cpp - Code for reading trace files.
//
// Copyright (c) 2018 Timothy Zhu.
// Licensed under the MIT License. See LICENSE file for details.
//

#include <iostream>
#include <fstream>
#include <string>
#include <cstdio>
#include <cstring>
#include <pthread.h>
#include "TraceReader.hpp"
#include "time.hpp"

using namespace std;

TraceReader::TraceReader(string filename)
    : _curIndex(0)
{
    double timestamp; // in microseconds
    char requestType[32];
    unsigned long requestSize; // in bytes
    unsigned long long index; 
    ifstream file(filename.c_str());
    pthread_mutex_init(&_mutex, NULL);
    if (file.is_open()) {
        string line;
        while (getline(file, line)) {
            // Parse line
            //cout<<"line = "<< line<<endl;
            int param_number = sscanf(line.c_str(), "%lf %s %lx %llu", &timestamp, requestType, &requestSize, &index);
            //cout<<"param_number = "<< param_number<<endl;
            if (param_number == 4) {
                // Store results 
                TraceEntry entry;
                // Scale to nanoseconds
                entry.arrivalTime = (uint64_t) (timestamp * NS_PER_SEC);
                entry.requestType = requestType;
                entry.requestSize = requestSize;
                entry.index = index; 
               // cout<<" arrival time= "<< entry.arrivalTime<<" requestType= "<< entry.requestType<<" request_size="
               // <<entry.requestSize<<" index= "<<index<<endl; 
                _trace.push_back(entry);
            }
        }
        file.close();
        cout<<"File loading completed."<<endl;
    } else {
        cerr << "Unable to open " << filename << endl;
    }
}

TraceReader::~TraceReader()
{
    pthread_mutex_destroy(&_mutex);
}

bool TraceReader::nextEntry(TraceEntry& entry)
{
    bool result = true;
    pthread_mutex_lock(&_mutex);
    if (_curIndex < _trace.size()) {
        entry = _trace[_curIndex++];
    } else {
        result = false;
    }
    pthread_mutex_unlock(&_mutex);
    return result;
}

void TraceReader::reset()
{
    pthread_mutex_lock(&_mutex);
    _curIndex = 0;
    pthread_mutex_unlock(&_mutex);
}