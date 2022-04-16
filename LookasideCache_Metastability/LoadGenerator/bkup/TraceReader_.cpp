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
#include <random>
#include "time.hpp"

using namespace std;
#define LAMBDA 100
#define EXPERIMENT_TIME 10 // seconds

std::default_random_engine generator;
std::exponential_distribution<double> distribution(LAMBDA);

TraceReader::TraceReader(uint64_t tracer_start_time)
    : _curIndex(0),_request_counter(0) 
{
   // _experiment_end_time = tracer_start_time + EXPERIMENT_TIME * NS_PER_SEC;
   _experiment_end_time = GetTime() + EXPERIMENT_TIME * NS_PER_SEC; 
    // cout<<"V first " << GetTime()<<" "<< experiment_end_time <<endl;
}

TraceReader::~TraceReader()
{
    pthread_mutex_destroy(&_mutex);
}

bool TraceReader::nextEntry(TraceEntry& entry)
{ 
    //cout<<GetTime()<<" "<< experiment_end_time <<endl;
    if(GetTime() > _experiment_end_time){
        return false; 
    }
    else{
        pthread_mutex_lock(&_mutex);
        double arrival_time = distribution(generator) * NS_PER_SEC; 
        entry.arrivalTime = arrival_time;
        entry.requestType = "0";
        pthread_mutex_unlock(&_mutex);
    }
    return true;
}

void TraceReader::reset()
{
    pthread_mutex_lock(&_mutex);
    _curIndex = 0;
    pthread_mutex_unlock(&_mutex);
}

void TraceReader::increment_request_counter(){
    _request_counter++;
}

void TraceReader::reset_request_counter(){
    _request_counter = 0;
}

int TraceReader::get_request_count(){
    return _request_counter;
}