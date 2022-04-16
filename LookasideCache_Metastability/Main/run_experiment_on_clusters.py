import json
import subprocess
from threading import Thread
import os
import sys 
import json  
import time
SQL_VM_AMI = "ami-0fd92c808c04c62a4"
GENERIC_AMI = "ami-04505e74c0741db8d"

ACCESS_KEY_ID = ""
SECRET_KEY_ID = ""
os.environ['AWS_ACCESS_KEY_ID'] = ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = SECRET_KEY_ID
MAIN_VM_IP= ""

def get_aws_config():   
    return f"export AWS_ACCESS_KEY_ID=\"{ACCESS_KEY_ID}\";  export AWS_SECRET_ACCESS_KEY=\"{SECRET_KEY_ID}\"; "

def get_cmd_aws_launch_instance(name, instance_type, AMI_ID):
    return get_aws_config() + "  aws ec2 run-instances --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value= " + name +  "}]' --image-id "+ AMI_ID +" --count 1 --instance-type " + instance_type + " --key-name  lookaside_cache_key --security-group-ids sg-0b08f66f95fab5814 --subnet-id subnet-471a8823 > instance_data.json"

cluster_file_prefix = "cluster_data_"

def create_cluster(cluster_id, name):   
    print("Creating cluster: "+  str(cluster_id))
    cluster_information = {}
    cluster_info_file_name = cluster_file_prefix + str(cluster_id) + ".txt"
    with open(cluster_info_file_name, "w") as cluster_file:
        
        os_command = get_cmd_aws_launch_instance("ClusterID_"+ str(name) + "_LoadGen", "m5.large", GENERIC_AMI) 
        subprocess.check_output(os_command, shell = True) 
        with open("instance_data.json") as instance_file:
            data = json.load(instance_file) 
            cluster_information["LOADGEN_IPV4"] = data["Instances"][0]["PrivateIpAddress"]
            cluster_information["LOADGEN_IP"] = data["Instances"][0]["PrivateIpAddress"]
            cluster_file.write(data["Instances"][0]["InstanceId"] + "\n")
        instance_file.close()


        os_command = get_cmd_aws_launch_instance("ClusterID_"+ str(name) + "_SQL", "c5.large", SQL_VM_AMI)    
        subprocess.check_output(os_command, shell = True)

        with open("instance_data.json") as instance_file:
            data = json.load(instance_file) 
            cluster_information["SQL_IPV4"] = data["Instances"][0]["PrivateIpAddress"]
            cluster_information["SQL_IP"] = data["Instances"][0]["PrivateIpAddress"]
            cluster_file.write(data["Instances"][0]["InstanceId"] + "\n")
        instance_file.close()
        

        os_command = get_cmd_aws_launch_instance("ClusterID_"+ str(name) + "_Memcached", "m5.large", GENERIC_AMI)    
        subprocess.check_output(os_command, shell = True)

        with open("instance_data.json") as instance_file:
            data = json.load(instance_file) 
            cluster_information["CACHE_IPV4"] = data["Instances"][0]["PrivateIpAddress"]
            cluster_information["CACHE_IP"] = data["Instances"][0]["PrivateIpAddress"]
            
            cluster_file.write(data["Instances"][0]["InstanceId"] + "\n")
        instance_file.close()       

        os_command = get_cmd_aws_launch_instance("ClusterID_"+ str(name) + "_WebServer", "m5.large", GENERIC_AMI)    
        subprocess.check_output(os_command, shell = True)

        with open("instance_data.json") as instance_file:
            data = json.load(instance_file) 
            cluster_information["WEB_IPV4"] = data["Instances"][0]["PrivateIpAddress"]
            cluster_information["WEB_IP"] = data["Instances"][0]["PrivateIpAddress"]
            cluster_file.write(data["Instances"][0]["InstanceId"] + "\n")
        instance_file.close()
    cluster_file.close()
    cluster_information["MAIN_VM_IP"] = MAIN_VM_IP

    with open(f"config_file_cluster{cluster_id}.json", "w+") as outfile:
        json.dump(cluster_information, outfile)

    if(os.path.exists("instance_params.json")):
        os.remove("instance_params.json")
        
    with open("instance_params.json", "w+") as outfile:
        json.dump(cluster_information, outfile)

    return cluster_information
    

def destroy_cluster(cluster_id):
    print("Terminating cluster: " + str(cluster_id))
    with open(cluster_file_prefix + str(cluster_id) + ".txt") as cluster_file:
        for line in  cluster_file:
            cmd_arg = "sudo aws ec2 terminate-instances --instance-ids " + line.rstrip()
            subprocess.check_output(cmd_arg, shell = True)
    cluster_file.close()

    if(os.path.exists(f"config_file_cluster{cluster_id}.json")):
        os.remove(f"config_file_cluster{cluster_id}.json")

path_to_rsa_key = "cache_workers.pem"
 
#CLUSTER_ID = 1000
#dictionary = create_cluster(CLUSTER_ID)
#destroy_cluster(CLUSTER_ID)
#with open(f"config_file_cluster{CLUSTER_ID}.json") as file:
#     dictionary = json.load(file)
# sudo python3 run_experiment_single.py 500 -1 1800 1.01 192 100  False

user = "ubuntu" 
EXP_DURATION = 30 
NUM_THREADS = 192
TRIGGER_OFFSET= 15
IS_CLOSED_LOOP_TEST = False

with open("general_exp_params.json") as commonExpParamFile:
    data = json.load(commonExpParamFile)
    EXP_DURATION = data["EXP_DURATION"]
    NUM_THREADS = data["NUM_THREADS"]
    TRIGGER_OFFSET= data["TRIGGER_OFFSET"]
    if(data["IS_CLOSED_LOOP_TEST"] == "False"):
        IS_CLOSED_LOOP_TEST = False
    else:
        IS_CLOSED_LOOP_TEST = True

    

# extract range of loads from the test config file 
# extract range of triggers for each load

test_type =  sys.argv[1:][0] 
if(len(sys.argv[1:]) != 1):
    print("Please pass test type. e.g.: timeout for timeout_test, hitrate for hitrate_test")
    quit()

dictionary_timeout_test = {"alpha": 1.00001}
dictionary_hitrate_test = {"timeout": 1}
loads_rps = []

if test_type == "timeout":
    file_name = "config_file_timeout_test.json"
elif test_type == "hitrate":
    file_name = "config_file_hitrate_test.json"
else:
    print("unknown type")
    quit()

with open(file_name) as jsonFile:
    data = json.load(jsonFile)
    if(test_type == "hitrate"):
        dictionary_timeout_test["timeout1"] = data["timeout1"]
        dictionary_timeout_test["timeout2"] = data["timeout2"]
    elseif(test_type == "timeout"):
        dictionary_hitrate_test["alpha1"] = data["alpha1"]
        dictionary_hitrate_test["alpha2"] = data["alpha2"]
        
    loads_rps = data["load"]

# -1 correspond to the highest trigger size (100% drop in cache hit rate)
#trigger_sizes = [1, 10, 100, 100* sqrt(10), 1000, 1000 * sqrt(10), 10000, 10000 * sqrt(10), 100000, 100000 * sqrt(10), 1000000, -1]

#"
#os.system(run_setup_instances_command)

#172.31.10.82
run_setup_instances_command = "python3 setup_instances.py;"

def run_experiment(LDGEN_IP, load, trigger, alpha, testtype):
    try:
        run_experiment_command = f"cd Metastability; cd LoadGenerator; sudo python3 run_experiment.py {load} {trigger} {EXP_DURATION} {alpha} {NUM_THREADS} {TRIGGER_OFFSET} {IS_CLOSED_LOOP_TEST} {TIMEOUT} {testtype}"
        cmd  = f"sudo ssh -o StrictHostKeyChecking=no -i {path_to_rsa_key} -p 22 {user}@{LDGEN_IP} \"{run_experiment_command}\"" 
        out = subprocess.check_output(cmd , shell= True)
        print(out)
    except subprocess.CalledProcessError as e:
        pass

iter = 0
default_alpha = 1.00001
trigger_sizes = [-1]
default_timeout = 1

print("Test type: " + test_type)

if test_type == "1":  
    timeouts = []
    timeouts.append(dictionary_timeout_test["timeout1"])
    timeouts.append(dictionary_timeout_test["timeout2"])
    
    for timeout in timeouts: 
        for load_rps in loads_rps:
            for trigger_size in trigger_sizes:
                create_cluster(iter)
                print("VMs instantiated")
                time.sleep(60)
                os.system(run_setup_instances_command)
                run_experiment(dictionary["LOADGEN_IPV4"],  load_rps, trigger_size, default_alpha, timeout, "alpha" + str(alphas.index(alpha))
                destroy_cluster(iter)
                iter+=1

else:
    alphas = []
    alphas.append(dictionary_hitrate_test["alpha1"])
    alphas.append(dictionary_hitrate_test["alpha2"])
    alphas = [1.14165]
    loads_rps = [100]
    for alpha in alphas:
        for load_rps in loads_rps:
            for trigger_size in trigger_sizes:
                dictionary = create_cluster(iter) 
                print("VMs instantiated")
                time.sleep(60)
                os.system(run_setup_instances_command)
                run_experiment(dictionary["LOADGEN_IPV4"],load_rps, trigger_size, alpha, default_timeout, "alpha" + str(alphas.index(alpha)))
                destroy_cluster(iter)
                iter+=1


#run_experiment(dictionary["LOADGEN_IPV4"])