# coding: macros

macro def MY_MACRO(a, b):
    print(a, b)

MY_MACRO("1", "6")

macro = macros.get_macro("MY_MACRO")

macro.execute("2", "4")

print("macro code:")
print(macro.code) # untokenized code

print("macro arguments:")
print(macro.args) # no args

print("\n\ntranslated to after preprocesser: \n")

print(macros.get_translated_code())