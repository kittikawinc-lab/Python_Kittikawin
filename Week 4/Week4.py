'''
# Fizz-Buzz Guide
x = int(input("Input your number :"))
if x % 3 == 0:
    print("Fizz")
elif x % 5 == 0:
    print("Buzz")
elif x % 15 == 0:
    print("Fizz - Buzz")
else:
    print("ERROR! please enter new number")

#Shorten if - else

me = 24
myfriend = 30
print("I am older than you") if me > myfriend else print ("No!") 

score = int(input("Input your score :"))
print("YOU PASS!") if score >= 50 else print("YOU FAIL!")

x = str(input("Will you marry me ? (yes/no):"))
print("Let's get married! (>3<)") if x == "yes" else print("I'm sad! (T_T)") 

#Shorten elif
x,y = 24,30 #there don't have "elif" in shorten form
print("Older") if x > y else print("Equal") if x == y else print("No") # If first condition is 'False' program will move to next condition

x = str(input("Input your gender (M / F / Others):"))
print("You are 'MALE' (-_-)") if x == "M" else print("You are 'FEMALE' (Q-Q)") if x == "F" else print("You are 'LGBTQ+' (>-<)")

#Nested if (Use 'if' in 'if')
x = int(input("Enter your age :"))
if x >= 7:
    if x <= 12:
        print("Elementary school")
    elif x <= 18:
        print("High school")
    else:
        print("Older")
else:
    print("Pre-school")

#While
while(True):
    print('i love you')

i = 1
z = 2
while(i < 13):
    print(str(z)+'x'+str(i)+'='+str(z*i))
    i += 1
'''
i = int(input('Input your number :'))
z = 1
while(z < 13):
    print(str(i)+'x'+str(z)+'='+str(z*i))
    z += 1

