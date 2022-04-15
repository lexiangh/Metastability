#!/bin/bash

rps=$1
trigger_duration=$2 # in ms
experiment_duration=$3 # in second
auto_detection_enabled=$4 # positive integer indicates "true"
maxheapsize=$5 #e.g., 256m

image_name="exp"
container_name="exp_container"

# Remove existing containers
sudo docker stop ${container_name}
sudo docker rm ${container_name}
sudo docker volume rm -f $(sudo docker volume ls -qf dangling=true)
sudo docker image prune -f

sudo docker create -it -m=1g --name ${container_name} ${image_name} /bin/bash
sudo docker start ${container_name}
sudo docker cp GCMetastability.java ${container_name}:/gc_artifacts/GCMetastability.java
sleep 2

sudo docker exec ${container_name} /bin/bash -c "
javac GCMetastability.java && java -XX:MaxHeapSize=${maxheapsize} -XX:+CrashOnOutOfMemoryError -XX:+PrintGC -XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:+PrintGCApplicationStoppedTime -Xloggc:gc.log GCMetastability ${rps} ${trigger_duration} ${experiment_duration} ${auto_detection_enabled} &
sleep 2;
vmid=\$(jps | grep GCMetastability | awk '{print \$1}');
jstat -gcutil -t \${vmid} 100 > gc.csv;
exit
"

sudo docker cp ${container_name}:/gc_artifacts/job.csv .
sudo docker cp ${container_name}:/gc_artifacts/gc.log .
sudo docker cp ${container_name}:/gc_artifacts/gc.csv .
sudo docker cp ${container_name}:/gc_artifacts/exp_record.csv .

