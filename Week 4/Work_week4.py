'''
#excercise 1
print("\n-------------------------","\nShoes calculater program!","\n-------------------------")
x = int(input("How many shoes that you buy ? (1:pair) :"))
if x == 2:
    print("We have promotion for you!","\n-------------------------")
    x1 = int(input("How much of your first shoes ? :"))
    x2 = int(input("How much of your second shoes ? :"))
    p = x1 + x2
    if (p >= 5000) and (p < 7000):
        print("-------------------------","\n > You've got 10 percent sale promotion!")
        c = p - ((p*10)/100)
        print("You have to paid",c,"on promotion cost!")
    elif (p >= 7000) and (p < 10000):
        print("-------------------------","\n > You've got 20 percent sale promotion!")
        c = p - ((p*20)/100)
        print("You have to paid",c,"on promotion cost!")
    elif p >= 10000:
        print("-------------------------","\n > You've got 30 percent sale promotion!")
        c = p - ((p*30)/100)
        print("You have to paid",c,"on promotion cost!")
    else:
        print("Sorry, There's no promotion for this order.")
else:
    x1 = int(input("-------------------------","\nHow much of your shoes ? :"))
    print("Sorry, There's no promotion for this order.")
'''
#excercise 2
print("\n-------------------------","\nDistance charges calculate program","\n-------------------------")
print (" 1 for 'Surcharge' payment","\n 2 for 'Lump sum' payment")
p = str(input("Choose your charges program [1/2] :"))
       
if p == "1":
    s = int(input("What is your distance ? (Kilometers): "))
    if s <= 25:
        print("\n------------------------- \nYou need to pay 25 baht for this distance")
    else:
        print("\n------------------------- \nYou have to pay 2 baht : kilometers \nthat you drive more than 25 kilometers \n-------------------------")
        ss = ((s - 25)*2)+25
        print("You need to pay",ss,"baht for this distance")
else:
     l = int(input("What is your distance ? (Kilometers):"))
     if l <= 25:
         print("\n------------------------- \nYou need to pay 25 baht for this distance")
     else:
         print("You drive more than 25 kilometers, \nYou need to pay 55 baht for this distance")
   
