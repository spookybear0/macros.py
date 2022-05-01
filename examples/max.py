# coding: macros

macro def MAX(a, b):
    (a if a > b else b)
    
macro def noargs:
    print("no args works!")

# print the max of 1 and 5
def max_1_and_5():
    print(MAX(1, 5))

max_1_and_5()

# print the max of 3 and 16
def max_3_and_16():
    print(MAX(3, 16))
    
max_3_and_16()

noargs