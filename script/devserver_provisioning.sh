sudo apt-get update -y

sudo apt-get install python -y
sudo apt-get install python-pip -y
sudo apt-get install mecab-ipadic-utf8 -y
sudo apt-get install python-mecab -y
sudo apt-get install redis-server -y


cd /vagrant; sudo make setup;
