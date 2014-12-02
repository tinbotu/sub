clean:
	find . -name "*.py[co]" -delete

setup:
	virtualenv . --system-site-packages
	./bin/pip install -r requirements.txt

status:
	service redis-server status

test:
	./bin/python tests.py
