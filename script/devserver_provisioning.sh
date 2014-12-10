sudo apt-get update -y

sudo apt-get install python -y
sudo apt-get install python-dev -y
sudo apt-get install python-pip -y
sudo apt-get install python-virtualenv -y
sudo apt-get install mecab-ipadic-utf8 -y
sudo apt-get install libmecab-dev -y
sudo apt-get install redis-server -y


cd /vagrant; sudo make setup;
