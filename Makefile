test-install:
	virtualenv _test-install-virtualenv
	. _test-install-virtualenv/bin/activate && pip install pytest
	. _test-install-virtualenv/bin/activate && pip install .
	. _test-install-virtualenv/bin/activate && cd testing && time python -m pytest -s

devel-install:
	virtualenv _devel-install-virtualenv
	. _devel-install-virtualenv/bin/activate && pip install pytest pudb
	. _devel-install-virtualenv/bin/activate && pip install -e .

build-package:
	pipenv run python setup.py sdist

upload-package:
	pipenv run python -m twine upload dist/*

run-unit_tests:
	. _devel-install-virtualenv/bin/activate && cd testing && time python -m pytest -s

run-cli_tests:
	. _devel-install-virtualenv/bin/activate && cd testing && time cram *.t

run-tests:
	make test-install
	make run-unit_tests
	make run-cli_tests
