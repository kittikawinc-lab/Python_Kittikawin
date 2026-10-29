'''
#For loop (Nested loops)
department = ['comed','scied','mathed']
university = ['kku','cmu','cu']
for x in department:
    for y in university:
        print(x +''+ y)

#Python function
#function = group of command 'def'(Defind) = way to cast function
def introduce():
    print('Hello im function')
    print('i will do nothing at all')
    print('Call me if you need help')
introduce()

#Python argument
def introduce(names):
    print("Hello, i'm " +names)
a = input("What's your name: ")
introduce(a)

def introduce(province, nation):
    print('Hello, i come from '+ province +',' + nation )
p = input('What province you came from ?:')
n = input('What nation are you ?:')
introduce(p,n)

def introduce(province, nation = 'thailand'):
    print('Hello, i come from '+ province +',' + nation )
introduce('khonkaen','usa')
introduce('khonkaen')

#keyword argument (kwarg)
def introduce(arg1,arg2 = 'com',arg3 = 'ed',arg4 = 'kku'):
    print('Hello, i am '+arg1+','+arg2+''+arg3+''+arg4)
introduce('python') #will change 'arg1' to 'python'
introduce(arg1 = 'python') #will definitly change 'arg1' to 'python' 
introduce(arg1 = 'python',arg3 = 'sci') #will definitly change 'arg1' to 'python' and definitly change 'arg3' to 'sci'
introduce('python',arg4 = 'cmu') #will change 'arg1' to 'python' and definitly change 'arg4' to 'cmu'
'''
#Arbitary argument
#if add '*' front of argument will set it to 'tuple'
#if add '**' front of argument will set it to 'dictionary'
def introduce(name, *hobby, **address):
    print('Hello, i am '+name+'.')
    print('My address :')
    for kw in address:
        print(kw + ':'+address[kw])
    print('My hobby :')
    for arg in hobby:
        print(arg)
introduce('Boss','drawing','listen to music','play game', province = 'khonkaen', nation = 'Thailand')