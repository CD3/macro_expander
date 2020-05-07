test-install:
	virtualenv _test-install-virtualenv
	. _test-install-virtualenv/bin/activate && pip install .

build-package:
	pipenv run python setup.py sdist

upload-package:
	pipenv run twince upload dist/*

run-tests:
	make test-install
	. _test-install-virtualenv/bin/activate && cd testing && pytest
