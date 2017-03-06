.PHONY: lint run publish-test publish clean

lint:
				pylint aqara

test: lint
				pytest

run:
				python3 main.py

publish-test: test
				python setup.py sdist upload -r pypitest

publish: test
				python setup.py sdist upload -r pypi

clean:
				find . -name "*.pyc" | xargs -I {} rm -v "{}"
