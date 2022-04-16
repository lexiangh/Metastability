#!/bin/bash
sudo sed -i 's/max_execution-time/;max_execution_time/' /etc/php/7.2/fpm/php.ini
echo "max_execution-time = $1" >> /etc/php/7.2/fpm/php.ini

sudo sed -i 's/request_terminate_timeout/;request_terminate_timeout/' /etc/php/7.2/fpm/pool.d/www.conf
echo "request_terminate_timeout= $1" >> /etc/php/7.2/fpm/pool.d/www.conf