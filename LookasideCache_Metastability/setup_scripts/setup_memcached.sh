sudo apt-get update
sudo apt-get -y install memcached
sudo apt-get -y install libmemcached-tools
sudo chmod 777 /etc/memcached.conf
sudo sed -i 's/-l 127.0.0.1/-l 0.0.0.0/' /etc/memcached.conf 
sudo sed -i 's/-m/#-m/' /etc/memcached.conf 
echo "-m $1" >> /etc/memcached.conf 
sudo service memcached restart
sudo apt-get -y install python3-pip
sudo pip3 install pymemcache

sudo sed -i "/warm_up_size =/c\warm_up_size = $2" ../Memcached\ codes/warm_up_cache.py
sudo mv ../Memcached\ codes/warm_up_cache.py ~/warm_up_cache.py