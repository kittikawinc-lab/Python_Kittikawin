#test 1 input + print
a = int(input('Enter number 1: '))
b = int(input('Enter number 2: '))
print (a+b)

#test2 string
a = int(input('Enter number 1: '))
b = int(input('Enter number 2: '))
print (str(a)+"" +str(b))

#test3 if-elif-else
a = int(input('Enter number 1: '))
b = int(input('Enter number 2: '))
if a > b:
    print('a > b')
    print('OK')
elif a == b:
    print('a = b')
else:
    print('a < b')
#teat4 print

w,x,y,z = 5,'Computer','Education',6
print(x)
print(y)
print(x + y)
print('I am student of ',x,'',y)
print(w + z)

#test5 info section practice
x,y,z = 20,20.0,1j
print(type(x))
print(type(y))
print(type(z))

#test6 Type conversion pratice
x,y,z = 20,20.0,1j
print (float(x)) #20.0
print (int(y)) #20
print (int(z)) #1