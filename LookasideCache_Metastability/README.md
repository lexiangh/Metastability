## System Setup

We need 4 VMs / Servers to run this experiment for the following parts:-

1. Load Balancer 
2. Web Server
3. MySQL Server
4. Memcached Server 


Please run the following commands(with appropriate parameters) in each of the VMs to configure & install necessary packages.  

Important Parameters: 
WebServer Params:
    CACHE_IP
    DATABASE_QUERY_WEIGHT
    SQL_IP
SqlServer Params:
    WEB_IP
    DB_ENTRIES

LoadGenerator VM:
    CACHE_IP
    MAIN_VM_IP

Memcached Params:
    CACHE_WARMUP_SIZE
    CACHE_MEM_SIZE

Web Server VM:
sudo apt-get update && git clone https://github.com/SalmanEstyak/Metastability && cd Metastability &&  cd setup_scripts && sudo chmod +x setup_server.sh && ./setup_server.sh {SQL_IP} {CACHE_IP} {DATABASE_QUERY_WEIGHT}

SQL Server VM:
 sudo apt-get install git && sudo git clone https://github.com/SalmanEstyak/Metastability.git && cd Metastability && cd setup_scripts &&  sudo chmod +x setup_mysql.sh && ./setup_mysql.sh {WEB_IP} {DB_ENTRIES}"

Memcached Server VM:
sudo apt-get update && sudo apt-get install git  &&  sudo  git clone https://github.com/SalmanEstyak/Metastability.git && cd Metastability && cd setup_scripts &&  sudo chmod +x setup_memcached.sh && ./setup_memcached.sh {CACHE_MEM_SIZE} {CACHE_WARMUP_SIZE}"

Load Generator VM:
sudo apt-get update && git clone https://github.com/SalmanEstyak/Metastability.git && cd Metastability && cd setup_scripts && sudo chmod +x setup_client.sh && ./setup_client.sh {WEB_IP} {CACHE_IP} {DB_ENTRIES} {MAIN_VM_IP}"


After the VMs are setup and every VM has proper IPs to communicate with (the current implement assumes that all the VMs would share a single key to communicate). We can begin running experiments.


## Running Experiments

In the Load Generator VM, run the following command:

sudo python3 run_experiment.py load trigger duration_of_test zipf_parameter num_threads sleep_period_before_trigger timeout test_type 

Explanation of each parameter:

load: Requests Per Second
trigger: Trigger indicates a certain drop in cache hit rate. With -1 as the trigger, all cache entries are dropped. 
duration_of_test: Experiment run time
zipf_parameter: This controls the 
num_threads: Number of threads to be used in TraceReplay (e.g. value: 64, 128)
sleep_period_before_trigger (This dictates the timepoint where the trigger is applied)
timeout: This is the maximum time a request can run before it gets killed by the server.  
test_type: We can provide any name here. 