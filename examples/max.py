# coding: macros

!MAX(a, b) (a if a > b else b)

!other_macro print("test")

# print the max of 1 and 5
def max_1_and_5():
    print(MAX(1, 5))

max_1_and_5()

# print the max of 3 and 16
def max_3_and_16():
    print(MAX(3, 16))
    
max_3_and_16()

other_macro