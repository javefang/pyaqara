.PHONY: version lint run publish-test publish clean

lint:
				pylint aqara

test: lint
				pytest

run:
				python3 main.py

version:
				$(eval TAG := $(shell git describe --tags | sort | head -1))
				@echo $(TAG)

publish-test: test version
				VERSION=$(TAG) python setup.py sdist upload -r pypitest

publish: test
				VERSION=$(TAG) python setup.py sdist upload -r pypi

clean:
				find . -name "*.pyc" | xargs -I {} rm -v "{}"
