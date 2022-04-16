#!/bin/bash
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get -y install nginx

sudo add-apt-repository ppa:ondrej/php -y
sudo yes | sudo apt-get install php7.2-cli php7.2-fpm php7.2-curl php7.2-gd php7.2-mysql php7.2-mbstring zip unzip php7.2-memcache;
 sudo cp ../config_files/default /etc/nginx/sites-available/default;


sudo sed -i "s/DATABASE_SERVER_IP/$1/"  ../NGINX\ Web\ Server/www/html/index.php
sudo sed -i "s/MEMCACHED_SERVER_IP/$2/"  ../NGINX\ Web\ Server/www/html/index.php
sudo sed -i "s/DATABASE_QUERY_WEIGHT/$3/"  ../NGINX\ Web\ Server/www/html/index.php
 

sudo sed -i "s/DATABASE_SERVER_IP/$1/" ../NGINX\ Web\ Server/www/html/util/db_connect_test.php
sudo sed -i "s/MEMCACHED_SERVER_IP/$2/" ../NGINX\ Web\ Server/www/html/util/memcached_throughput_test.php

#copy all server codes to appropriate folder
sudo rm -r /var/www/html/*
sudo cp -r ../NGINX\ Web\ Server/www/html/* /var/www/html/

# set execution time
# set default execution time 1s
#set default request_termination time 1s
##/etc/php/7.2/fpm/php.ini  max_execution_time
#/etc/php/7.2/fpm/pool.d/www.conf
sudo chmod 777 /etc/php/7.2/fpm/php.ini
sudo chmod 777 /etc/php/7.2/fpm/pool.d/www.conf

sudo sed -i 's/max_execution-time/;max_execution_time/' /etc/php/7.2/fpm/php.ini
echo "max_execution-time = 1s" >> /etc/php/7.2/fpm/php.ini

sudo sed -i 's/request_terminate_timeout/;request_terminate_timeout/' /etc/php/7.2/fpm/pool.d/www.conf
echo "request_terminate_timeout= 1s" >> /etc/php/7.2/fpm/pool.d/www.conf

sudo service nginx reload
sudo service php7.2-fpm restart

ssh-keyscan $1  >> $HOME/.ssh/known_hosts
ssh-keyscan $2  >> $HOME/.ssh/known_hosts 
