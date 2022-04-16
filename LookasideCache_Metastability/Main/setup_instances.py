import json
import subprocess
from threading import Thread
import os
import sys 
import time

def os_ssh_keygen(IP):
    os_command = f"ssh-keyscan {IP}  >> $HOME/.ssh/known_hosts"
    os.system(os_command)

def setup_sql():
    try:
        #out = subprocess.check_output(["ssh", "-i", path_to_rsa_key, "-p", "22", "{}@{}".format(user, SQL_IPV4), mysql_ssh_command])
        cmd  = f"sudo ssh -o StrictHostKeyChecking=no -i {path_to_rsa_key} -p 22 {user}@{SQL_IPV4} \"{mysql_ssh_command}\"" 
        out = subprocess.check_output(cmd , shell= True)
        time.sleep(5)
    except subprocess.CalledProcessError as e:
        pass

def setup_memcached():
    try:
            #out = subprocess.check_output(["ssh", "-i", path_to_rsa_key, "-p", "22", "{}@{}".format(user, CACHE_IPV4), memcached_ssh_command])
            cmd  = f"sudo ssh -o StrictHostKeyChecking=no -i {path_to_rsa_key} -p 22 {user}@{CACHE_IPV4} \"{memcached_ssh_command}\""
            #print(cmd)
            out = subprocess.check_output(cmd , shell= True)
            time.sleep(5)
    except subprocess.CalledProcessError as e:
        pass

def setup_webserver():
    try:
            #out = subprocess.check_output(["ssh", "-i", path_to_rsa_key, "-p", "22", "{}@{}".format(user, WEB_IPV4), webserver_ssh_command]) 
            cmd  = f"sudo ssh -o StrictHostKeyChecking=no -i {path_to_rsa_key} -p 22 {user}@{WEB_IPV4} \"{webserver_ssh_command}\"" 
            out = subprocess.check_output(cmd , shell= True)
            time.sleep(5)
    except subprocess.CalledProcessError as e:
        pass

def setup_loadgen():
    try:
            #out = subprocess.check_output(["ssh", "-i", path_to_rsa_key, "-p", "22", "{}@{}".format(user, LOADGEN_IPV4), loadgen_ssh_command])
            cmd  = f"sudo ssh -o StrictHostKeyChecking=no -i {path_to_rsa_key} -p 22 {user}@{LOADGEN_IPV4} \"{loadgen_ssh_command}\"" 
            out = subprocess.check_output(cmd , shell= True)        
            local_file_path1 = 'cache_workers.pem'
            local_file_path2 = 'cache_workers.pem'
            connUser = 'ubuntu'
            connHost = master_host
            connPath1 = '/home/ubuntu/Metastability/LoadGenerator' + 'cache_workers.pem' 
            connPath2 = '/home/ubuntu/Metastability/LoadGenerator' + 'cache_workers.pem' 
            connPrivateKey = './cache_workers.pem'
            # Use scp to send file from local to host.
            scp = subprocess.Popen(['scp', '-i', connPrivateKey, local_file_path1, '{}@{}:{}'.format(connUser, connHost, connPath1)])
            scp = subprocess.Popen(['scp', '-i', connPrivateKey, local_file_path2, '{}@{}:{}'.format(connUser, connHost, connPath2)])
    except subprocess.CalledProcessError as e:
       pass
       

path_to_rsa_key = "cache_workers.pem"
user = "ubuntu"

CACHE_IPV4 = "127.0.0.1"
SQL_IPV4 = "127.0.0.1"
WEB_IPV4 = "127.0.0.1"
CACHE_IP = "127.0.0.1"
SQL_IP = "127.0.0.1"
WEB_IP = "127.0.0.1"
CACHE_MEM_SIZE = 1536
DB_ENTRIES =  34511000
CACHE_WARMUP_SIZE =  4000000
LOADGEN_IP = "127.0.0.1"

# Opening JSON file
with open('instance_params.json') as json_file:
    data = json.load(json_file)
    CACHE_IPV4 = data["CACHE_IPV4"]
    SQL_IPV4 = data["SQL_IPV4"]
    WEB_IPV4 = data["WEB_IPV4"]
    LOADGEN_IPV4 = data["LOADGEN_IPV4"]

    CACHE_IP = data["CACHE_IP"]
    SQL_IP = data["SQL_IP"]
    WEB_IP = data["WEB_IP"]
    LOADGEN_IP = data["LOADGEN_IP"]

with open("main_vm_ip.json") as main_vm_json:
    data = json.load(main_vm_json)
    MAIN_VM_IP = data["MAIN_VM_IP"]
 
   

with open("server_tuning_params.json") as experiment_json:
    data = json.load(experiment_json)
    CACHE_MEM_SIZE = data["CACHE_MEM_SIZE"]
    DB_ENTRIES =  data["DB_ENTRIES"]
    CACHE_WARMUP_SIZE =  data["CACHE_WARMUP_SIZE"]
    DATABASE_QUERY_WEIGHT = data["DATABASE_QUERY_WEIGHT"]

webserver_ssh_command = f"sudo apt-get update && git clone https://github.com/SalmanEstyak/Metastability && cd Metastability &&  cd setup_scripts && sudo chmod +x setup_server.sh && ./setup_server.sh {SQL_IP} {CACHE_IP} {DATABASE_QUERY_WEIGHT}"
mysql_ssh_command = f"sudo rm -r Metastability && sudo apt-get install git && sudo git clone https://github.com/SalmanEstyak/Metastability.git && cd Metastability && cd setup_scripts &&  sudo chmod +x setup_mysql.sh && ./setup_mysql.sh {WEB_IP} {DB_ENTRIES}"
memcached_ssh_command = f"sudo apt-get update && sudo apt-get install git  &&  sudo  git clone https://github.com/SalmanEstyak/Metastability.git && cd Metastability && cd setup_scripts &&  sudo chmod +x setup_memcached.sh && ./setup_memcached.sh {CACHE_MEM_SIZE} {CACHE_WARMUP_SIZE}"
loadgen_ssh_command = f"sudo apt-get update && git clone https://github.com/SalmanEstyak/Metastability.git && cd Metastability && cd setup_scripts && sudo chmod +x setup_client.sh && ./setup_client.sh {WEB_IP} {CACHE_IP} {DB_ENTRIES} {MAIN_VM_IP}"


t2 = Thread(target=setup_memcached)
t3 = Thread(target=setup_webserver)
t4 = Thread(target=setup_loadgen)
t1 = Thread(target=setup_sql)

t2.start()
t3.start() 
t4.start()
t1.start()
 
t2.join()
print("memcached configuration finished.")
t3.join() 
print("webserver configuration finished.")
t4.join()
print("loadgen configuration finished.")
t1.join() 
print("mysql configuration finished.")
 