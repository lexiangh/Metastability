primary=
secondary1=
secondary2=

pem_file=

[ -z "$primary" ] && echo "ERROR: set primary replica ip in config.sh" && exit 1
[ -z "$secondary1" ] && echo "ERROR: set secondary1 replica ip in config.sh" && exit 1
[ -z "$secondary2" ] && echo "ERROR: set secondary2 replica ip in config.sh" && exit 1
[ -z "$pem_file" ] && echo "ERROR: set pem file absolute address in config.sh" && exit 1

d=$(date +"%Y%m%d") #used to create output directory
