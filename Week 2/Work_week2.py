'''
#ecercise 2
num1 = float(input('Enter your first number: '))
num2 = float(input('Enter your second number: '))
num3 = float(input('Enter your third number: '))
num4 = float(input('Enter your forth number: '))
num5 = float(input('Enter your fifth number: '))
print ("Float of", int(num1), "equal",num1)
print("complex of", int(num1), "equal",complex(num1))
print ("Float of", int(num2), "equal",num2)
print("complex of", int(num2), "equal",complex(num2))
print ("Float of", int(num3), "equal",num3)
print("complex of", int(num3), "equal",complex(num3))
print ("Float of", int(num4), "equal",num4)
print("complex of", int(num4), "equal",complex(num4))
print ("Float of", int(num5), "equal",num5)
print("complex of", int(num5), "equal",complex(num5))

#exercise 3
num1 = int(input('Enter your first number: '))
num2 = int(input('Enter your second number: '))
print(num1,("="),num2,(":"),num1 == num2)


#excercise 4.1
Me = int(input('Enter your age: '))
Myfriend = int(input('Enter your friend age: '))
if Me > Myfriend :
    print("I am older than  you !")
else :
    print("You are older than me.")

#excercise 5
print("Day converter program")
D = (int(input("Input number of day ---> ")))
print(D,"Days ---> Hour",D*24,"Hours")
print(D,"Days ---> Minutes",D*24*60,"Minutes")
print(D,"Days ---> seconds",D*24*60*60,"seconds")
'''
#excercise 6
Bosslist = ["EN","CP","AG","HS","BS"]
print(Bosslist)
print(Bosslist[1])
print(Bosslist[-1])
print(Bosslist[1:3]) 
print(Bosslist[:3])
Bosslist.insert(1,"Hello")
print(Bosslist)
Bosslist.append("Hello")
print(Bosslist)
Bosslist.remove("Hello")
print(Bosslist)
Bosslist.remove(Bosslist[5])
print(Bosslist)
x = input("Add your word to this list :")
Bosslist.append(x)
print(Bosslist)