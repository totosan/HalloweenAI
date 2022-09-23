#!/bin/bash
#pip install wheel
python setup.py bdist_wheel --universal
pip wheel . -w wheelhouse