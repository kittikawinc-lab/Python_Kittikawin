#Function guide
def introduce(names):
    print('Hello i am',names)
introduce('Boss')

#lambda guide
def expo(n):
    return lambda p : n**p
expos = expo(2)
print(expos(5))

#lambda guide 2
def expo(n):
    return lambda p : n**p
power2 = expo(2)
power3 = expo(3)
print(power2(5))
print(power3(5))