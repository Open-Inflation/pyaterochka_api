python3 setup.py sdist
python3 -m venv __env__
__env__/bin/pip install twine
__env__/bin/twine upload dist/*