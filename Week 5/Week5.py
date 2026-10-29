'''
#While-Break
i = 1
z = 2
while(i < 13):
    print(str(z)+'x'+str(i)+'='+str(z*i))
    if i == 5:
        break #'break' will stop loop function in condition
    i += 1

i = 1
while(i < 13):
    print(i)
    i += 1
    break
'''
i = 0
z = 2
while(i < 12):
    i += 1
    if i == 5: # function will cut part in condition out
        continue #'continue' will cut out function flow in condition
    print(str(z)+'x'+str(i)+'='+str(z*i))
'''
#For-loop function
names = ['A','B','C','D'] #create list
for x in names: #'for' is for activate loop function in list
    print(x)

name = 'Python'
for x in name:
    print(x)

#Practice
a = []
while(True):
    b = input('Shop\nAdd [a]\n Show [s]\n Exit [x]\n')
    b = b.lower()
    if b == 'a':
        c = input('Insert customer ID (ID:Name:IGN)')
        a.append(c)
        print('\n Data saved \n')
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
