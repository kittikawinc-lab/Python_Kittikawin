
#1
name = input("Please enter your name:")
Height = float(input("Input your height (M):"))
Weight = float(input("Input your weight:"))
print("-------------------------------------------")
if Height > 3:
    Height = Height / 100
bmi =  Weight / Height**2
if bmi >= 30 :
    print(name,",your BMI =",bmi,"You are now at tier 2 FAT")
elif bmi >= 25.0  :
    print(name,",your BMI =",bmi,"You are now at tier 1 FAT")
elif bmi >= 23.0 :
    print(name,",your BMI =",bmi,"you are now at risk to be FAT tier")
elif bmi >= 18.5:
    print(name,",your BMI =",bmi,"You are in normal tier")
else:
    print(name,",your BMI =",bmi,"You are now at SLIM tier")

#2
def line():
     print('------------------------------------')

def pcl():
     print(' (+) function')
     line()
     total = n1 + n2
     print('The total of',n1,'+',n2,'=',total)
     line()
     r = input('Do you want to see more answer ? [y/n]:')
     if r =='y':
          re()
     else:
          print('Thanks you to use this program')

def ncl():
     print(' (-) function')
     line()
     total = n1 - n2
     print('The total of',n1,'-',n2,'=',total) 
     line()
     r = input('Do you want to see more answer ? [y/n]:')
     if r =='y':
         re()
     else:
         print('Thanks you to use this program') 

def xcl():
     print(' (x) function')
     line()
     total = n1 * n2
     print('The total of',n1,'x',n2,'=',total)
     line()
     r = input('Do you want to see more answer ? [y/n]:')
     if r =='y':
         re()
     else:
         print('Thanks you to use this program')

def kcl():
     print(' (/) function')
     line()
     total = n1 / n2
     print('The total of',n1,'/',n2,'=',total)
     line()
     r = input('Do you want to see more answer ? [y/n]:')
     if r =='y':
         re()
     else:
         print('Thanks you to use this program')

def re():
     return menu()

print('Number calculating program')
line()
n1 = int(input('Input your first number:'))
n2 = int(input('Input your second number:'))

def menu():
        print('---Number calculating program---')
        print('\n[1] (+)\n','[2] (-)\n','[3] (x)\n','[4] (/)')
        m = input('Choose your program :')
        if m == '1':
            pcl()
        elif m == '2':
            ncl()
        elif m == '3':
            xcl()
        elif m == '4':
            kcl()
        else:
              print("don't have this function")
menu()

#3
def line():
     print('------------------------------------')

def mcc():
     print('Cone mass calculating function')
     line()
     r = int(input('What is your cone radius?:'))
     h = int(input('What is your cone height?:'))
     line()
     total = (3.14*(r**2)*h)/3
     print('The total of cone mass is:',total)

def mco():
     print(' Circle calculating function')
     line()
     r = int(input('What is your cone radius?:'))
     line()
     total = (4*3.14*(r**3))/3
     print('The total of circle mass is:',total)

def menu():
        print('Mass calculating program')
        line()
        print('\n[1] Cone mass calculating function\n','[2] Circle calculating function\n')
        line()
        m = input('Choose your program :')
        if m == '1':
            mcc()
        elif m == '2':
            mco()
        else:
              print("don't have this function")
menu()
