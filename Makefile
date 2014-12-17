.PHONY: test clean setup deploy status lint

test:
	./bin/python tests.py

clean:
	find . -name "*.py[co]" -delete

setup:
	virtualenv .
	./bin/pip install -r requirements.txt

deploy:
	@echo -----------------------------------------------
	git pull -v origin master
	@echo -----------------------------------------------
	@git log -2
	@echo -----------------------------------------------
	./bin/pip install -r requirements.txt

status:
	sudo service redis-server status

lint:
	./bin/flake8 sun.cgi

