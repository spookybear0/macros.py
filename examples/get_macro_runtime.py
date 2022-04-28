# coding: macros

!MY_MACRO print("from macro")

MY_MACRO

macro = macros.get_macro("MY_MACRO")

print(macro)

print(macro.code) # untokenized code

print(macro.args) # no args