it:
	python3 setup.py build

testit:
	PYTHONPATH=. pytest-3

package: testit
	rm -rf dist
	python3 setup.py sdist bdist_wheel

publish:
	python3 -m twine upload -u __token__ dist/*

install:
	python3 setup.py install

# build a readme from rst files
README.md: docs/index.rst docs/usage.rst Makefile
	pandoc -i docs/index.rst -o docs/index.md
	cat docs/index.md | perl -p -e 'if (/:::/) { exit }' > $@
	pandoc -i docs/usage.rst -o docs/usage.md
	cat docs/usage.md >> $@
	rm -f docs/usage.md docs/index.md
