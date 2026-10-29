'''
#ecercise 2.3
a = []
while(True):
    print('-----------B beauty shop------------')
    b = input('Shop program \nAdd [a]\n Show [s]\n Exit [x]\n')
    b = b.lower()
    if b == 'a':
        c = input('Insert customer ID (ID:Name:IGN):')
        a.append(c)
        print('\n *******Data saved******* \n')
    elif b == 's':
        print('{0:-<6}{0:-<10}{0:-<10}'.format(""))
        print('{0:-<6}{1:-<10}{2:-<10}'.format('ID','Name','IGN'))
        print('{0:-<6}{0:-<10}{0:-<10}'.format(""))
        for d in a:
            e = d.split (":")
            print('{0[0]:<6}{0[1]:<10}{0[2]:<10}'.format(e))
            continue
    elif b == 'x':
        c = input('You want to close this program ? [y/n] :')
        if c == 'y':
            print('End program')
            break
        else:
            continue
'''
#excercise 4
clist = []
p = {
    '1':('Herb',15),
    '2':('Water',10),
    '3':('Noodle',20),
    '4':('Soap',18),
    '5':('Toothbrush',20)
}

def showp():
    print('----------Item lists----------')
    print('1. Herb\n','2. Water\n','3. Noodle\n','4. Soap\n','5. Toothpaste\n')

def addcart():
    showp()
    while(True):
        c = input('\nChoose your item (Press [x] to return to menu):')
        if c == 'x':
            break
        elif c == '1':
            print('Add ',p[c][0],'to your cart.')
            clist.append(p[c])
        elif c == '2':
                    print('Add ',p[c][0],'to your cart.')
                    clist.append(p[c])
        elif c == '3':
                    print('Add ',p[c][0],'to your cart.')
                    clist.append(p[c])
        elif c == '4':
                    print('Add ',p[c][0],'to your cart.')
                    clist.append(p[c])
        elif c == '5':
                    print('Add ',p[c][0],'to your cart.')
                    clist.append(p[c])
        else:
               print("Don't have that order")

def showc():
       print("\n----------Item in cart----------")
       if clist == 0:
              print("Don't have item in cart")
              return
       total = 0
       re = input('Do you want to remove item [PRESS y] (This will remove current item that you add to cart):')
       if re == 'y':
             clist.pop()
             print('This will remove current item that you add to cart')
             for name,price in clist:
                            print(name,'..........',price,'Baht')
                            total += price
             print('Total =',total,'Baht')       
       else:
               for name,price in clist:
                            print(name,'..........',price,'Baht')
                            total += price
               print('Total =',total,'Baht')
              
def menu():
       while(True):
        print('----------Online marget program----------')
        print('\n[1] Show items\n','[2] Pick items\n','[3] Show count & cost of your item\n','[x] Exit program')
        m = input('Choose your program :')
        if m == '1':
            showp()
        elif m == '2':
            addcart()
        elif m == '3':
            showc()
        elif m == 'x':
            print('Thank for use this program')
            break
        else:
              print("don't have this function")
menu()
              

            