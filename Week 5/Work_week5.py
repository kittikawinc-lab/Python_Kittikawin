'''
#ecercise 1.1
i = 0
mlist = []
m = 0
print('Please enter your favorits food (Type "exit" to close the program)')
while(True):
        i += 1
        if m != 'exit':
                m = input('Your favorite food is :')
                mlist.append(m)
        else:
            print('---------------------------------')
            mlist.remove('exit')

            for x in mlist:
                print('Your',i,'favorite food is :',x)
            break

#ecercise 1.2
i = 1
mlist = []
m = 0
print('Please enter your favorits food (Type "exit" to close the program)')
while(True):
        if m != 'exit':
                m = input(f'Your {i} favorite food is :')
                mlist.append(m)
                i += 1
        else:
            print('---------------------------------')
            mlist.remove('exit')
            print('Your favorite food is :',mlist)
            break

#ecercise 2
i = 0
p = int(input('Input your Peepo quantity :'))
while(True):
    if p >= 9:
        p -= 9
        i += 1
        print('Peepo',i,'pack')
        print('Still have',p,'\n')
    else:
        print('------------------------------------------')
        print('Have',i,'peepo pack in total')
        print('Still have',p,'peepo')
        break

#ecercise 2.2
i = 0
n = 0
print('Number calculating program')
while(i < 3):
     n = int(input('please enter your number:'))
     a = n + n
     i += 1
print('totalize of your number is:'a)
'''
#excercise 3.3.1
i = 0
clist =[]
while(True):
    print('+++Select your shoes+++\n')
    print('[1] Nike\n','[2] Adidas\n','[3] Reebok\n','[s] Show basket\n','[x] Return to main menu')
    m = input('Select your menu :')
    if m == '1':
        while(True):
            print('----------Nike----------')
            print('[1] Air max 97 : 5800\n','[2] Air jordan 1 : 3600\n','[3] Epic React Flynite : 5600\n','[x] Return to main menu')
            Ndic = {'1':('Air max 97 : 5800\n',5800),'2':('Air jordan 1 : 3600\n',3600),'3':('Epic React Flynite : 5600\n',5600)}
            N = input('Choose your order :')
            if N != 'x':
                clist.append(Ndic[N])
                print('Add',Ndic[N][0],'to your cart')
            else:
                break
    elif m == '2':
        while(True):
            print('----------Adidas----------')
            print('[1] Super star : 3200\n','[2] Ultras Booth : 7900\n','[3] Nemezis : 2350\n','[x] Return to main menu')
            Adic = {'1':('Super star : 3200\n',3200),'2':('Ultras Booth : 7900\n',7900),'3':('Nemezis : 2350\n',2350)}
            A = input('Choose your order :')
            if A != 'x':
                clist.append(Adic[A])
                print('Add',Adic[A][0],'to your cart')
            else:
                break
    elif m == '3':
        while(True):
            print('----------Reebok----------')
            print('[1] Energylux Driftium : 1690\n','[2] Royal Bridge : 2190\n','[3] Fabulista Mid II : 1190\n','[x] Return to main menu')
            Rdic = {'1':('Energylux Driftium : 1690\n',1690),'2':('Royal Bridge : 2190\n',2190),'3':('Fabulista Mid II : 1190\n',1190)}
            R = input('Choose your order :')
            if R != 'x':
                clist.append(Rdic[R])
                print('Add',Rdic[R][0],'to your cart')
            else:
                break
    elif m == 's':
        print('------Your cart------')
        total = 0
        for a in clist:
            print(a[0], 'Baht')
            total += a[1]
        print('-------------------------------------')
        print('total =',total,'Baht')
    elif m == 'x':
        print('\nBack to main menu\n')
        break



        





        

