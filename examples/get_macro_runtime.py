# coding: macros

!MY_MACRO print("from macro")

MY_MACRO

print(macros.get_macro("MY_MACRO"))