FROM ubuntu:20.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        openjdk-8-jdk \
        python3-pip \
        && apt-get clean && rm -rf /var/lib/apt/lists/* \
        && pip3 install pandas \
        && pip3 install matplotlib

RUN mkdir /gc_artifacts
WORKDIR /gc_artifacts