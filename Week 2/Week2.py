'''
#Syntax guide
print ("x = ",int(20)) #20
print ("y = ",int(35.24)) #35
print ("z = ",int("35")) #35

print ("x = ",float(20)) #20.0
print ("y = ",float(35.24)) #35.24
print ("z = ",float("35")) #35.0

print ("x = ",str(20)) #20
print ("y = ",str(35.24)) #35.24
print ("z = ",str("Hello")) #Hello
#Assigning Guide
x = """ Lorem Ipsum is simply dummy text of the printing and typesetting industry.
 Lorem Ipsum has been the industry’s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. 
It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged.
 It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, 
and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum"""
print(x)

#Array_collection (if/else)
Me = 24
Myfriend = 30
if Me > Myfriend :
    print("I am older than  you !")
else :
    print("You are older than me.")

#Array_collection (Booleen)
print(bool("python"))

#Assignment_Operaters
x = ["comed","kku"] #1st object
y = ["comed","kku"] #2nd object
z = x # use same object as 1st
print(x is z)
print(x is y) # = false. bc x and y doesn't use same object
print(x is not y)
print("kku" in x) #find object in 1st
print("ku" in x)

#Bitwise_Operaters
a = 60 #0011 1100
b = 13 #0000 1101
c = 0
c = a & b #0000 1100
print(c)
c = a | b #0011 1101
print(c)
c = a ^ b #0011 0001
print(c)
c = ~a #1100 0011
print(c)
c = a << 2 #1111 0000
print(c)
c = a >> 2 #0000 1111
print(c)
'''
#List guide
thislist = ["com","ed","kku",99] #list set as 0 1 2 3
print(thislist)
print(thislist[1])
print(thislist[-1])
print(thislist[1:3]) #Only count before 1st index to before last index
print(thislist[:3]) #same as 1:3 but count first index too
thislist[2] = "msu" 
print(thislist)