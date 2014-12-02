clean:
	find . -name "*.py[co]" -delete

setup:
	virtualenv .
	./bin/pip install -r requirements.txt

test:
	./bin/python tests.py
