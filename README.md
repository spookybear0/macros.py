# macros.py

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/macros.py.svg)](https://badge.fury.io/py/macros.py)
[![PyPI downloads](https://img.shields.io/pypi/dm/macros.py)](https://badge.fury.io/py/macros.py)
[![Repo Size](https://img.shields.io/github/repo-size/spookybear0/macros.py)](https://github.com/spookybear0/macros.py)


## Macros in python

macros.py is an implemention of macros similar to ones found in C using a custom codec to implement a feature into python

Guido van Rossum would hate me


## Examples

### Max function-macro
```py
# coding: macros

macro def MAX(a, b):
    (a if a > b else b)

# print the max of 1 and 5
def max_1_and_5():
    print(MAX(1, 5))

max_1_and_5()

# output:
# 5
```

This code gets translated to python-readable code:

```py
# coding: macros

# print the max of 1 and 5
def max_1_and_5():
    print((1 if 1 > 5 else 5))

max_1_and_5()

# output:
# 5
```

More examples can be found in the examples directory

## How it works

~Magic~

Macros are possible due to a quirk in python that allows custom encodings to be created and preprocess the code before it is run. When a macro is defined it doesn't actually define it as a python variable, it saves the bytecode and name of a macro in a list of macros that is checked against when token of type `tokenize.NAME` is seen. When a macro is used, it yields the tokens of the macro in place (and if the macro has args, replaces those).

## Installing

### From pip
```sh
py -m pip install -U macros.py
```

### From source
```sh
git clone https://github.com/spookybear0/macros.py
cd macros.py
python3 -m pip install -U .
```


## A side note
This library is a joke, please do not ever use this in a real project.

This code is also of terrible quality, but I might decide to improve it soon
