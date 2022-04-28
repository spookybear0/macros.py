# coding: macros

!DEFINE_MYNEWFUNC def mynewfunc():\
    print("it works!!1!1!");\
    print("two statements in one??")

def test():
    print("from test")
    DEFINE_MYNEWFUNC
    # uses locally defined function
    mynewfunc()
    
test()
    
try:
    # since its defined locally it only works in test()
    mynewfunc()
except NameError:
    print("doesn't exist")