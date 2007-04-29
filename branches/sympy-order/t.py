from sympy import *

x = Symbol("x")
w = Symbol("w")
#e=((2*w)/w)**(1+w)
#print e.series(w,1)

#e=(sin(2*w)/w)
#print e.series(w,2)


x=Symbol("x")
w=Symbol("w")

#some limits need this series expansion to work:
e=(w**(-log(5)/log(3))-1/w)**(1/x)
print  e.series(w,1)

#assert e.series(w,1).subs(w,0)==2
#print Order(w**2).diff(w)
#print Order(2*w)
#print Order(1).sym

#fix this:

#raises exception:
#print e.series(x,6) + Order(x**7)

#this should return False
#print Order(x**7).is_number

#raises exception:
#e=(sin(2*w)/w)**(1+w)
#print e.series(w,3)

#test this:

#Order(x) == -Order(x)
#returns O(1)+ O(1).., or similar nonsense
#assert ((1/x+1)**3).series(x,4)== x**(-3)+3*x**(-2)+3*x**(-1)
