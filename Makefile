.PHONY: test clean setup deploy status lint

test:
	./bin/python tests.py

clean:
	find . -name "*.py[co]" -delete

setup:
	python3 -m venv .
	./bin/pip install --upgrade pip
	./bin/pip install -r requirements.txt

update_packages:
	./bin/pip install -r requirements.txt

status:
	sudo service redis-server status

lint:
	./bin/flake8 sun.py subculture tests.py

