'''
#excercise 5.1
class nisit :
    def __init__(self,name,gender,syear,sclass):
        self.name = name
        self.gender = gender
        self.syear = syear
        self.sclass = sclass

    def shownisit(self):
        x.asknisit()
        print('---------Introduce---------')
        print('Hello, my name is',self.name,"I'm",self.gender)
        print("I'm studied at",self.syear,'grade in university')
        print('and i am studied at',self.sclass)

    def asknisit(self):
        self.name = str(input('What is your name ?:'))
        self.gender = str(input('What is your gender ?:'))
        self.syear = str(input('What is your studied year ?:'))
        self.sclass = str(input('What is your faculty ?:'))
        
x = nisit('name','gender','syear','sclass')
x.shownisit()
'''
#excercise 5.2

class shop :
    def __init__(self):
        self.p = []

    def addshop(self):
        print('-----Add products------')
        p = input('What is your product ?:')
        c = input('What is it cost ?:')
        self.p.append([p,c])
        print('Add',p,'finished')
        r = input('Do you want to add more product ? [y/n]:')
        if r == 'y':
            return self.addshop()
        else:
            return

    def showshop(self):
        for p,c in self.p:
            print(p,'___________',c,'Baht')

    def menu(self):
       while(True):
         print('-----Fullchunk restaurant-----')
         print('\n[1] Show items\n','[2] Add items\n','[x] Exit program')
         m = input('Choose your program :')
         if m == '1':
             self.showshop()
         elif m == '2':
             self.addshop()
         elif m == 'x':
             print('Thank for use this program')
             break
         else:
              print("don't have this function")
              return self.menu()
y = shop()
y.menu()

