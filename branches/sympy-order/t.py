from sympy import *

x = Symbol("x")
w = Symbol("w")
#e=((2*w)/w)**(1+w)
#print e.series(w,1)

#e=(sin(2*w)/w)
#print e.series(w,2)

e=(sin(2*w)/w)**(1+w)
print e.series(w,3)

#assert e.series(w,1).subs(w,0)==2
#print Order(w**2).diff(w)
#print Order(2*w)
#print Order(1).sym

#fix this:
#raises exception:
#print e.series(x,6) + Order(x**7)
#this should return False
#print Order(x**7).is_number

#test this:

#Order(x) == -Order(x)
