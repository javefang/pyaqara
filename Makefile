.PHONY: lint run publish-test publish

lint:
				pylint aqara

run:
				python3 main.py

publish-test: lint
				python setup.py sdist upload -r pypitest

publish: lint
				python setup.py sdist upload -r pypi
