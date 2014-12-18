sudo apt-get update -y

sudo apt-get install python -y
sudo apt-get install python-dev -y
sudo apt-get install python-pip -y
sudo apt-get install python-virtualenv -y
sudo apt-get install mecab-ipadic-utf8 -y
sudo apt-get install libmecab-dev -y
sudo apt-get install redis-server -y

sudo apt-get install git -y

sudo locale-gen ja_JP.UTF-8
sudo /usr/sbin/update-locale LANG=ja_JP.UTF-8

cd /vagrant; sudo make setup;
