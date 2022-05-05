# coding: macros

macro def print(arg):
    print(arg, end="")

macro def println(arg):
    print(arg)

print("no line break\n")

println("with line break")