#
# Logan build script
#

clean:
	find . -name '*.pyc' -exec rm --force {} +

lint:
	# See http://flake8.pycqa.org/en/latest/index.html#quickstart
	flake8 app.py

run:
	python app.py

sec:
	bandit app.py

install:
	pip install -r requirements.txt

createenv:
	virtualenv .