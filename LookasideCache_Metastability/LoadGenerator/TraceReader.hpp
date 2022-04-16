// // TraceReader.hpp - Class definitions for reading trace files.
// //
// // Copyright (c) 2018 Timothy Zhu.
// // Licensed under the MIT License. See LICENSE file for details.
// //

// #ifndef _TRACE_READER_HPP
// #define _TRACE_READER_HPP

// #include <string>
// #include <vector>
// #include <stdint.h>
// #include <pthread.h>

// using namespace std;

// struct TraceEntry {
//     uint64_t arrivalTime; // in nanoseconds
//     string requestType; // request type
//     uint32_t requestSize; // in bytes
// };

// class BaseTraceReader
// {
// public:
//     BaseTraceReader() { }
//     virtual ~BaseTraceReader() { }

//     // Fills entry with the next request from the trace. Returns false if end of trace.
//     virtual bool nextEntry(TraceEntry& entry) = 0;
//     // Resets trace reader back to beginning of trace.
//     virtual void reset() = 0;

//     virtual void increment_request_counter() = 0;
//     virtual void reset_request_counter() = 0;
//     virtual int get_request_count() = 0;
// };

// // Reads and stores requests from trace file on construction.
// // Trace file must be in CSV format with one request per line. Each line contains 5 columns:
// // 1) (decimal) arrival time of request in microseconds
// // 2) (string) request type
// // 3) (hex) number of bytes in request
// class TraceReader : public BaseTraceReader
// {
// private:
//     pthread_mutex_t _mutex;
//     vector<TraceEntry> _trace;
//     unsigned int _curIndex;
//     uint64_t _experiment_end_time;
//     uint64_t _experiment_start_time;
//     uint64_t _request_counter; 
    
// public:
//     TraceReader(uint64_t tracer_start_time);
//     virtual ~TraceReader();

//     virtual bool nextEntry(TraceEntry& entry);
//     virtual void reset();
//     virtual void increment_request_counter();
//     virtual void reset_request_counter();
//     virtual int get_request_count();
// };

// #endif // _TRACE_READER_HPP

// TraceReader.hpp - Class definitions for reading trace files.
//
// Copyright (c) 2018 Timothy Zhu.
// Licensed under the MIT License. See LICENSE file for details.
//

#ifndef _TRACE_READER_HPP
#define _TRACE_READER_HPP

#include <string>
#include <vector>
#include <stdint.h>
#include <pthread.h>

using namespace std;

struct TraceEntry {
    uint64_t arrivalTime; // in nanoseconds
    string requestType; // request type
    uint32_t requestSize; // in bytes
    uint64_t index; 
};

class BaseTraceReader
{
public:
    BaseTraceReader() { }
    virtual ~BaseTraceReader() { }

    // Fills entry with the next request from the trace. Returns false if end of trace.
    virtual bool nextEntry(TraceEntry& entry) = 0;
    // Resets trace reader back to beginning of trace.
    virtual void reset() = 0;
};

// Reads and stores requests from trace file on construction.
// Trace file must be in CSV format with one request per line. Each line contains 5 columns:
// 1) (decimal) arrival time of request in microseconds
// 2) (string) request type
// 3) (hex) number of bytes in request
class TraceReader : public BaseTraceReader
{
private:
    pthread_mutex_t _mutex;
    vector<TraceEntry> _trace;
    unsigned int _curIndex;

public:
    TraceReader(string filename);
    virtual ~TraceReader();

    virtual bool nextEntry(TraceEntry& entry);
    virtual void reset();
};

#endif // _TRACE_READER_HPP