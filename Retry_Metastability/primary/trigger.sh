#sample usage
#bash mongo.sh 10 5 .5 1
#runs 10 seconds, then trigger executes for 5 seconds at 0.5 cpu then back to full cpu

untilTrigger="$1"
triggerDuration="$2"
triggerCPU="$3"
finalCPU="$4"

#date +%s%N
sudo docker update --cpus "$finalCPU" primary
sleep "$untilTrigger"
sudo docker update --cpus "$triggerCPU" primary
sleep "$triggerDuration"
sudo docker update --cpus "$finalCPU" primary

