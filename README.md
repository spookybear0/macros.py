# macros.py

## Macros in python

macros.py is an implemention of macros similar to ones found in C using `!` to define macros

Guido van Rossum would hate me

## Examples

### Max function-macro
```py
# coding: macros

!MAX(a, b) (a if a > b else b)

# print the max of 1 and 5
def max_1_and_5():
    print(MAX(1, 5))

max_1_and_5()

# output:
# 5
```

More examples can be found in the examples directory

## How it works

You might be wondering, how the hell did you make macros in python. It's possible due to a quirk in python that allows custom encodings to be created and preprocess the code before it is run. When a macro is defined it doesn't actually define it as a python variable, it saves the bytecode and name of a macro in a list of macros that is checked against when token of type `tokenize.NAME` is seen. When a macro is used, it yields the tokens of the macro in place (and if the macro has args, replaces those).

<!--- not on PyPi yet
## Installing

To install you must run the following command:
```
py -3 -m pip install -U macros.py
```
-->
## Installing

### From source
```sh
git clone https://github.com/spookybear0/macros.py
cd macros.py
python3 -m pip install --upgrade .
```


## A side note
This library is a joke, please do not ever use this in a real project.

This code is also of terrible quality, but I might decide to improve it soon
