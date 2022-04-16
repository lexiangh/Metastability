// time.hpp - Time related helper functions.
//
// Copyright (c) 2018 Timothy Zhu.
// Licensed under the MIT License. See LICENSE file for details.
//

#ifndef _TIME_HPP
#define _TIME_HPP

#include <ctime>
#include <time.h>
#include <stdint.h>
#include <iostream>

using namespace std;

#define NS_PER_SEC 1000000000ull

// Converts seconds to nanoseconds
inline uint64_t ConvertSecondsToTime(double sec)
{
    return (uint64_t)(sec * (double)NS_PER_SEC);
}

// Convert nanoseconds to seconds
inline double ConvertTimeToSeconds(uint64_t t)
{
    return (double)t / (double)NS_PER_SEC;
}

// Converts timespec to nanoseconds
inline uint64_t ConvertTimespecToTime(struct timespec* t)
{
    return (uint64_t)t->tv_sec * NS_PER_SEC + (uint64_t)t->tv_nsec;
}

// Converts nanoseconds to timespec
inline void ConvertTimeToTimespec(uint64_t t, struct timespec* out)
{
    out->tv_sec = t / NS_PER_SEC;
    out->tv_nsec = t % NS_PER_SEC;
}

// Gets monotonic time
inline uint64_t GetTime()
{
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    return ConvertTimespecToTime(&now);
}

// Sleeps until specified time
inline void AbsoluteSleep(uint64_t t)
{
    struct timespec request;
    ConvertTimeToTimespec(t, &request);
    //cout<<"sleep, t= "<< t<<" nano seconds, tv_sec = "<< request.tv_sec <<" seconds" <<endl;
    clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &request, NULL);
}

// Sleeps for specified time
inline void RelativeSleep(uint64_t t)
{
    struct timespec request;
    ConvertTimeToTimespec(t, &request);
    clock_nanosleep(CLOCK_MONOTONIC, 0, &request, NULL);
}

// Sleeps until specified time even if there are signal interrupts
inline void AbsoluteSleepUninterruptible(uint64_t t)
{
    while (GetTime() < t) {
        AbsoluteSleep(t);
    }
}

// Sleeps for specified time even if there are signal interrupts
inline void RelativeSleepUninterruptible(uint64_t t)
{
    AbsoluteSleepUninterruptible(GetTime() + t);
}

// Print the current date/time in human-readable format.
inline void printTime()
{
    time_t t;
    time(&t);
    cout << ctime(&t);
}

#endif // _TIME_HPP
