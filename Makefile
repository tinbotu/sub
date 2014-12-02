clean:
	find . -name "*.py[co]" -delete

setup:
	# Install python packages to system python
	pip install -r requirements.txt

status:
	service redis-server status

test:
	python tests.py
