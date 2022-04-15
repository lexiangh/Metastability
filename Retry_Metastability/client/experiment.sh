source config.sh

while getopts "p:c:n:i:r:s:d:t:o:f:" flag
do
    case "${flag}" in
        p) primary=${OPTARG};;
        c) collection=${OPTARG};;
        n) n=${OPTARG};;
        i) requestInterval=${OPTARG};;
        o) timeOut=${OPTARG};;
        r) requestResends=${OPTARG};;
        s) untilTrigger=${OPTARG};;
        d) triggerDuration=${OPTARG};;
        t) triggerCpu=${OPTARG};;    
        f) fileName=${OPTARG};;         
    esac
done



mkdir -p $d

./mongoC3 -primary=$primary -collection=$collection -n=$n -interval=$requestInterval \
          -timeout=$timeOut -resends=$requestResends    2>> $d/${fileName} &
ssh -i $pem_file -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@$primary  "bash  primary/trigger.sh $untilTrigger $triggerDuration $triggerCpu 2"
