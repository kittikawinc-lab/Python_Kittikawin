'''
#excercise 1.1
bossset = {"A","B","C","D","E"}
for x in bossset:
    print(x) #Set function dont have index thats why info will be random when print

#excercise 1.2
bossset = {"A","B","C","D","E","E"}
for x in bossset:
    print(x) #Set function dont have index thats why info will be random when print

#excercise 2.3 A
print("---------------------------------------")
print("\tItem list program")
print("---------------------------------------")
cart = []
cart.append("Soap")
cart.append("Toothpaste")
cart.append("Candy")
cart.append("Water")
cart.append("Noodle")
print("Your fist item is :",cart[0])
print("Your second item is :",cart[1])
print("Your third item is :",cart[2])
print("Your forth item is :",cart[3])
print("Your fifth item is :",cart[4])
print("------------------------------------------")
print("All of your item in cart -->")
for x in cart:
    print(x)
'''
#excercise 2.3 B
print("------------------------------------------")
print("Item list program -->")
print("------------------------------------------")
cart = []
x1 = input("Add your first item to list :")
cart.append(x1)
x2 = input("Add your second item to list :")
cart.append(x2)
x3 = input("Add your third item to list :")
cart.append(x3)
x4 = input("Add your forth item to list :")
cart.append(x4)
x5 = input("Add your fifth item to list :")
cart.append(x5)
print("------------------------------------------")

print("Your fist item is :",cart[0])
print("Your second item is :",cart[1])
print("Your third item is :",cart[2])
print("Your forth item is :",cart[3])
print("Your fifth item is :",cart[4])

print("------------------------------------------")

print("All of your item in cart -->")
'''
for x, cart in enumerate(cart, start=1): #enumirate is function to make counting system to item in list #start is function to begin counting from x
    print(f"{x}.{cart}") 
'''
print("1.",x1)
print("2.",x2)
print("3.",x3)
print("4.",x4)
print("5.",x5)
'''
#excercise 2.4
print("Motorway cost program")
print("---------------------------------------------")
costdic = {
    "1":"Vehicle with 4 wheels cost \n Lardkrabang --> Bangbor...25...baht \n Lardkrabang --> Bangprakong...30...baht \n Lardkrabang --> Panassanikhom...45...baht \n Lardkrabang --> Baanbueng...55...baht \n Lardkrabang --> Bangpra...60...baht",
    "2":"Vehicle with 6 wheels cost \n Lardkrabang --> Bangbor...40...baht \n Lardkrabang --> Bangprakong...45...baht \n Lardkrabang --> Panassanikhom...75...baht \n Lardkrabang --> Baanbueng...90...baht \n Lardkrabang --> Bangpra...100...baht",
    "3":"Vehicle with <6 wheels cost \n Lardkrabang --> Bangbor...60...baht \n Lardkrabang --> Bangprakong...70...baht \n Lardkrabang --> Panassanikhom...110...baht \n Lardkrabang --> Baanbueng...130...baht \n Lardkrabang --> Bangpra...140...baht"
}
print("Vehicle with 4 wheels press 1 \n Vehicle with 6 wheels press 2 \n Vehicle with >6 wheels press 3 \n") 
x = (input("Chosse yor Vehicle type:"))
print("---------------------------------------------")
print(costdic[x])

#excercise 3
print("Distance cost counter (Kilometers) \n ------------------------------------------")
print("Choose menu \n +++++++++++++++++++++++++++++++++++++")
print("Press 1 for Lump sum payment \n Press 2 for pay more payment")
'''