# Set-up

For the Mongo experiment, we create 4 virtual machines in AWS.  Three replica servers and a client machine.  
* **Replica servers**  AWS EC2 m5a.large with 2 vCPU and 8Gib RAM. Called:
    * primary
    * secondary1
    * secondary2

* **Client** AWS EC2 m5ad.2xlarge 8 vCPU and 32 Gib RAM
 
 For all machines, the code files are expecting the username to be **ubuntu** for connecting.  
 
 
## AWS Environment Access ##
Evaluator can contact authors for access to a vm environment set up in AWS where the client and replicas are already set-up and configured to run the experiments, otherwise steps for setting up vm environment provided below. 

 

 
## Client machine
1. Create virtual machine in AWS in a region
 * Amazon Machine Image - Ubuntu Server 20.04 LTS (HVM), SSD Volume Type 64-bit(x86)
 * Instance type - m5ad.2xlarge
 * For security group:
    * Add custom TCP rule inbound allow port 27017
	* Allow SSH inbound
 * Install:  
    1. Upload client folder to client home directory. Contains files
        * mongoC3.go
	   * experiment.sh
        * experiments.sh
    2. Upload private key required to access the primary replica to client machine 
    3. Update experiment.sh for replica server ip address (you will need to do this after creating the replica machine and it is recommended to use private IPv4 addresses) and private key absolute path
	3. Change permissions on pem file
	<pre>chmod 400 evaluator.pem</pre> **Or modify for filename of uploaded private key file**
    4. Install go and compile go client
                
<pre>echo installing go
curl -OL https://golang.org/dl/go1.16.7.linux-amd64.tar.gz
sudo tar -C /usr/local -xvf go1.16.7.linux-amd64.tar.gz
printf '\nexport PATH=$PATH:/usr/local/go/bin\n' >> ~/.profile
source ~/.profile
go version
</pre>

<pre>echo creating client
cd client
go mod init example.com
go mod tidy
go build mongoC3.go
</pre>

2. Create replicas (3 total) in the same region as client
* Amazon Machine Image - Ubuntu Server 20.04 LTS (HVM), SSD Volume Type 64-bit(x86)
* Instance type - m5a.large
 * For security group:
    * Add custom TCP rule inbound allow port 27017
	* Allow SSH inbound
	Install: 1) Docker on each replica

<pre>
echo installing docker
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
yes | sudo apt-get install docker-ce docker-ce-cli containerd.io
</pre>

3. Customize Primary
    1. Upload primary folder to home directory of primary replica
	2. Modify config.js for the ip addresses of each replica. It is recommended to use the private Ipv4 address


Environment is now setup



# Usage

* Log into client vm.  
*Execute 
<pre>cd client
bash experiments.sh</pre>

**NOTE: there is some variability in the outcome of the experiments due to the stochastic nature of replicating a metastable failure. You may need to run the experiments more than once to replicate the behavior observed for the paper.**

**NOTE: if after repeating experiments you find that, the baseline case does not recover after the trigger you may need to adjust the request frequency up. If the metastable case does recover after the trigger you may need to adjust the request frequency down. We found that tuning the request frequency maybe required to demonstrate the different behaviors of the system.**



*  Each experiment corresponds to one experiment performed in the paper.
    1. **baseline** corresponds to  a) Baseline with no metastable failure trigger 10 sec, -78% CPU
    1. **metastable** corresponds to b) Increased trigger magnitude causes metastable failure 10 sec, -80% CPU
    1. **no_metastable1** corresponds to c) Decreased trigger aversts metastable failure, 9 sec, -80% CPU
    1. **no_metastable2** corresponds to d) Reduced load averts metastable failure, 10 sec, ~80% CPU, -30% RPS

The output of each experiment is written to a log file in a date stamped directory in the client directory.  The output of the log is tab delimited with the following fields:
1. time stamp of log entry
1. process id
1. retry attempts
1. succ or err (representing successful or errror request)
1. latency (microseconds)

A tool has been provided to plot the results of the experiment. It is available at https://colab.research.google.com/drive/1kt0pWFr98l9FzynWoTXtG9OvR725R7Mv?usp=sharing
