.PHONY: test clean setup deploy status lint

test:
	./bin/python tests.py

clean:
	find . -name "*.py[co]" -delete

setup:
	virtualenv --python=$(which python3) .
	./bin/pip install -r requirements.txt

update_packages:
	./bin/pip install -r requirements.txt

status:
	sudo service redis-server status

lint:
	./bin/flake8 sun.cgi

