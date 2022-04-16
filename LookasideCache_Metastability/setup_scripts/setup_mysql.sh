#!/bin/bash
# echo "params: $1 $2" 
# sudo chmod 777  /var/cache/debconf/config.dat
# sudo cat ../config_files/deb_conf.dat >>  /var/cache/debconf/config.dat
# sudo wget http://repo.mysql.com/mysql-apt-config_0.8.10-1_all.deb
# sudo DEBIAN_FRONTEND=noninteractive dpkg -i mysql-apt-config_0.8.10-1_all.deb
# sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 467B942D3A79BD29
# sudo apt-get update 
# sudo apt update
# sudo apt install -y mysql-client=5.7.*-1ubuntu18.04
# sudo debconf-set-selections <<< 'mysql-community-server mysql-community-server/root-pass password hello@123'
# sudo debconf-set-selections <<< 'mysql-community-server mysql-community-server/re-root-pass password hello@123'
# sudo DEBIAN_FRONTEND=noninteractive apt install -y mysql-community-server=5.7.*-1ubuntu18.04
# sudo DEBIAN_FRONTEND=noninteractive apt install -y mysql-server=5.7.*-1ubuntu18.04
# sudo mysql -u root -phello@123 < init_database.sql

# sudo sed -i "s/.*bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mysql.conf.d/mysqld.cnf
# sudo /etc/init.d/mysql stop
# sudo /etc/init.d/mysql start

# sudo wget https://github.com/Percona-Lab/mysql_random_data_load/releases/download/v0.1.12/mysql_random_data_load_0.1.12_Linux_x86_64.tar.gz
# sudo tar -xvf  mysql_random_data_load_*
# ./mysql_random_data_load metastable_test_db large_test_table $2  --user=root --password=hello@123
# wget random data generator , run it with params
# construct a mini sql file from here
# for adding server IP, user to mysql

# adding webserver IP
# sudo sed -i "/SET @a:=/c\SET @a:= $2;" linearize_column_data.sql
# sudo sed -i "s/remote_server_ip/$1/" add_user.sql
# sudo ufw allow 3306
# sudo mysql -u root -phello@123 < add_user.sql
# sudo mysql -u root -phello@123 < linearize_column_data.sql

# echo "params: $1 $2" 
#sudo chmod 777  /var/cache/debconf/config.dat
#sudo cat ../config_files/deb_conf.dat >>  /var/cache/debconf/config.dat
#sudo wget http://repo.mysql.com/mysql-apt-config_0.8.10-1_all.deb
#sudo DEBIAN_FRONTEND=noninteractive dpkg -i mysql-apt-config_0.8.10-1_all.deb
#sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 467B942D3A79BD29
#sudo apt-get update 
#sudo apt update
#sudo apt install -y mysql-client=5.7.*-1ubuntu18.04
#sudo debconf-set-selections <<< 'mysql-community-server mysql-community-server/root-pass password hello@123'
#sudo debconf-set-selections <<< 'mysql-community-server mysql-community-server/re-root-pass password hello@123'
#sudo DEBIAN_FRONTEND=noninteractive apt install -y mysql-community-server=5.7.*-1ubuntu18.04
#sudo DEBIAN_FRONTEND=noninteractive apt install -y mysql-server=5.7.*-1ubuntu18.04
#sudo mysql -u root -phello@123 < init_database.sql

#sudo sed -i "s/.*bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mysql.conf.d/mysqld.cnf
#sudo /etc/init.d/mysql stop
#sudo /etc/init.d/mysql start

#sudo wget https://github.com/Percona-Lab/mysql_random_data_load/releases/download/v0.1.12/mysql_random_data_load_0.1.12_Linux_x86_64.tar.gz
#sudo tar -xvf  mysql_random_data_load_*
#./mysql_random_data_load metastable_test_db large_test_table $2  --user=root --password=hello@123
# wget random data generator , run it with params
# construct a mini sql file from here
# for adding server IP, user to mysql

# adding webserver IP
#sudo sed -i "/SET @a:=/c\SET @a:= $2;" linearize_column_data.sql

#sudo mysql -u root -phello@123 < linearize_column_data.sql
 
sudo touch new_user.sql
sudo chmod 777 new_user.sql
sudo echo "CREATE USER 'metastable'@'$1' IDENTIFIED BY 'hello@123';" > new_user.sql
sudo echo "GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT, REFERENCES, RELOAD on *.* TO 'metastable'@'$1' WITH GRANT OPTION;" >> new_user.sql
sudo echo "FLUSH PRIVILEGES;" >> new_user.sql 
 
#sudo ufw allow 3306
sudo mysql -u root -phello@123 < new_user.sql