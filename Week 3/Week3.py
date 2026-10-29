'''
#List command guide
thislist = ["com","ed","kku",99] 
del thislist[3]
print(thislist)
#del thislist #delete all in list even list name (program will not define 'thislist')
thislist.clear()
print(thislist)

#List tuple
thistuple = ("com","ED","KKU") #Tuple collection cannot change info in list [use '( )' to make tuple list]
print(thistuple)
print(thistuple[1])
print(thistuple[-1])
print(thistuple[0:1])

#Change tuple info
x = ("com","ED","KKU")
y = list(x)
print(x,"|",y)
y[0] = "comED"
x = tuple(y)
print(x,"|",y)

#Delete tuple info
x = ("com","ED","KKU")
del x
print(x)

#Set collection
thisset = {"com","ED","KKU","KKU"} #'Set' will not count same info
print(thisset)
for x in thisset: #use 'x' for activate loop function
    print(x) #info in set will be keep in 'x' and will cast one by one

#Set add function
thisset = {"com","ED","KKU",}
thisset.add("Hello")
print(thisset)
thisset.update(["I","am","the","Flash"])
print(thisset) #Set function dont have index thats why info will be random when print

#Set delete function
thisset = {"com","ED","KKU",}
thisset.remove("com")
print(thisset)
thisset.discard("ED")
print(thisset)
thisset.clear()
print(thisset)
#del thisset
'''
#Function dictionary
thisdic = {
    "fname" : "Kittikawin",
    "lname" : "Chanbuttarach",
    "year" : 2007
}
x = thisdic["fname"]
print(x)
print(thisdic)
thisdic["year"] = 2026
print(thisdic)
thisdic["nation"] = "thai"
print(thisdic)
thisdic.pop("year") #Delete this item 
thisdic.popitem() #Delete new added item
print(thisdic)
#del thisdic
'''
#If-else statement
Me = 24
Myfriend = 30
if Me > Myfriend :
    print("I am older than you !")
else :
    print("You are older than me.")

Me = 35
Myfriend = 30
if Me > Myfriend :
   print("I am older than you !")
else :
        print("You are older than me.")

#Grade counter program
x = int(input("Input your score:"))
if x > 100 :
    print("Your score are WRONG")
elif x >= 80 :
    print("Your grade is : A")
elif x >= 75 :
    print("Your grade is : B+")
elif x >= 70 :
    print("Your grade is : B")
elif x >= 65 :
    print("Your grade is : C+")
elif x >= 60 :
    print("Your grade is : C")
elif x >= 55 :
    print("Your grade is : D+")
elif x >= 50 :
    print("Your grade is : D")
else:
    print("Your grade is : F")
'''
#BMI counter program
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