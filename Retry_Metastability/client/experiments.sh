source config.sh


#starts up the mongo replica environment
start_servers() {
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${primary} 'sudo docker run -p 27017:27017 -d --name primary mongo:4.4.9 --replSet rsmongo'
  sleep 5
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${primary} 'sudo docker cp ./primary/config.js primary:/config.js'
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${secondary1} 'sudo docker run -p 27017:27017 -d --name secondary1 mongo:4.4.9 --replSet rsmongo'  
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${secondary2} 'sudo docker run -p 27017:27017 -d --name secondary2 mongo:4.4.9 --replSet rsmongo'  
  sleep 5
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${primary} 'sudo docker exec  primary mongo localhost:27017 /config.js'
  sleep 15
}

#removes mongo container instances
stop_servers() {
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${primary} 'sudo docker stop primary && sudo docker rm primary'
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${primary} 'sudo docker volume rm $(sudo docker volume ls -qf dangling=true)'
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${secondary1} 'sudo docker stop secondary1 && sudo docker rm secondary1'
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${secondary1} 'sudo docker volume rm $(sudo docker volume ls -qf dangling=true)'
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${secondary2} 'sudo docker stop secondary2 && sudo docker rm secondary2'  
  ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@${secondary2} 'sudo docker volume rm $(sudo docker volume ls -qf dangling=true)'
}

pause() {
#pauses until log file stops being updated
while :

do
  echo 'waiting to end'
  sleep 3
  newRead=$(ls -l $d | grep $fn)
  echo $newRead
  if [ "$read" = "$newRead" ]; then
     break
  fi
  read=$newRead
  
done
sleep 5

}

exec_experiment() {
initialWait=$1
triggerLength=$2
triggerCpu=$3
interval=$4
n=$5
retry=$6

fn=$(echo "mongo_${initialWait}_${triggerLength}_${triggerCpu}_${interval}_${retry}.log")

start_servers
bash experiment.sh -i $interval -s $initialWait -d $triggerLength -t $triggerCpu -r $retry -f $fn -n $n -o 3 -c t1
pause
stop_servers

}

stop_servers

#baseline
echo baseline

initialWait=60
triggerLength=10
triggerCpu=0.45
interval=75000
n=1000000
retry=4

exec_experiment $initialWait $triggerLength $triggerCpu $interval $n $retry


#metastable
echo metastable
initialWait=60
triggerLength=10
triggerCpu=0.40
interval=75000
n=1000000
retry=4

exec_experiment $initialWait $triggerLength $triggerCpu $interval $n $retry

#not metastable 9 sec


echo not metastable 9 sec
initialWait=60
triggerLength=9
triggerCpu=0.40
interval=75000
n=1000000
retry=4

exec_experiment $initialWait $triggerLength $triggerCpu $interval $n $retry

#not metastable reduced rate

echo not metastable reduced rate
initialWait=60
triggerLength=10
triggerCpu=0.40
interval=100000
n=1000000
retry=4

exec_experiment $initialWait $triggerLength $triggerCpu $interval $n $retry

echo done
