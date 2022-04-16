#!/bin/bash
sudo apt-get update;
sudo apt -y install build-essential;
sudo apt-get -y install python3-pip;
sudo pip3 install matplotlib
sudo pip3 install scipy
sudo pip3 install pymemcache
sudo pip3 install SciencePlots
 
sudo sed -i "/string ngnix_server_ip =/c\string ngnix_server_ip =\"$1\";" ../LoadGenerator/TraceReplay.cpp
sudo sed -i "/memcached_host =/c\memcached_host = \'$2\'" ../LoadGenerator/run_experiment.py 
sudo sed -i "/master_host =/c\master_host = \'$4\'" ../LoadGenerator/run_experiment.py 

sudo sed -i "/memcached_host =/c\memcached_host = \'$2\'" ../LoadGenerator/trigger_size_k.py
sudo sed -i "/row_nums_in_db =/c\row_nums_in_db = $3" ../LoadGenerator/TraceFileGenerator.py
mkdir ../LoadGenerator/traces
mkdir ../LoadGenerator/results_warm_cache
mkdir ../LoadGenerator/result_stats 
mkdir ../LoadGenerator/experiment_plots
cd ../LoadGenerator && make
sudo chmod 600 ../config_files/cache_workers.pem
sudo cp ../config_files/cache_workers.pem ../LoadGenerator/cache_workers.pem

ssh-keyscan $1  >> $HOME/.ssh/known_hosts
ssh-keyscan $2  >> $HOME/.ssh/known_hosts
ssh-keyscan $4  >> $HOME/.ssh/known_hosts