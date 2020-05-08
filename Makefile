test-install:
	virtualenv _test-install-virtualenv
	. _test-install-virtualenv/bin/activate && pip install pytest
	. _test-install-virtualenv/bin/activate && pip install .

build-package:
	pipenv run python setup.py sdist

upload-package:
	pipenv run python -m twine upload dist/*

run-tests:
	make test-install
	. _test-install-virtualenv/bin/activate && cd testing && python -m pytest -s
	. _test-install-virtualenv/bin/activate && cd testing && cram *.t
