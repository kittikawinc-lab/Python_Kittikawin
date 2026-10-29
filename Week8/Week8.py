'''
#class guide
class classname :
    name = "I'm Mr. class"
    id = "This is ID"
x = classname()
print(x.name)
print('and',x.id)

#init function
class car :
    def __init__(self,name,colour):
        self.name = name
        self.colour = colour
x = car('civic','blue')
y = car('toyota','red')
print('this car is',x.name)
print('it is',x.colour)
print(y.name,y.colour)

class car :
    def __init__(self,name,colour,model):
        self.name = name
        self.colour = colour
        self.model = model

    def showcar(self):
        print('Car information')
        print('Name:',self.name)
        print('Colour:',self.colour)
        print('Version:',self.model)

x = car('Mecedes Benz','black','RX7')
x.showcar()

#Class object create
class car :
    def __init__(self,name,colour):
        self.name = name
        self.colour = colour

    def showcar(self):
        print('Car information')
        print('Name:',self.name)
        print('Colour:',self.colour)

x = car('Mecedes Benz','black')
x.colour = 'Grey'
#del x.colour
x.showcar()
print(x.colour)

#Class parent,child
class car () : 
    def __init__(self,name,colour):
            self.name = name
            self.colour = colour

    def showcar(self):
            print('Car information')
            print('Name:',self.name)
            print('Colour:',self.colour)

class newcar(car) :
       pass

x = newcar('Lambogini','yellow')
x.showcar()
## __init__ child class
class car () : 
    def __init__(self,name,colour):
            self.name = name
            self.colour = colour

    def showcar(self):
            print('Car information')
            print('Name:',self.name)
            print('Colour:',self.colour)

class newcar(car) :
     def __init__(self,name,colour):
            car.__init__(self,name,colour)

x = newcar('Lambogini','yellow')
x.showcar()

#super class function
class car () : 
    def __init__(self,name,colour):
            self.name = name
            self.colour = colour

    def showcar(self):
            print('Car information')
            print('Name:',self.name)
            print('Colour:',self.colour)

class newcar(car) :
     def __init__(self,name,colour,gear):
            super().__init__(name,colour)
            self.gear = gear #Add more parameter

x = newcar('Lambogini','yellow','auto')
print(x.gear)
x.showcar()
##def in Childclass
class car () : 
    def __init__(self,name,colour):
            self.name = name
            self.colour = colour

    def showcar(self):
            print('Car information')
            print('Name:',self.name)
            print('Colour:',self.colour)
            line()

class newcar(car) :
     def __init__(self,name,colour,gear):
            super().__init__(name,colour)
            self.gear = gear #Add more parameter

     def showcar2(self):
                 print('Car information')
                 print('Name:',self.name)
                 print('Colour:',self.colour)
                 print('Gear:',self.gear)
                 line()

def line():
       print('----------------------------')

x = newcar('Lambogini','yellow','auto')
x.showcar()
x.showcar2()
'''
#Try-except (Excution function) (If-else for recheck codding phase)
try:
    print('Hello'+5)
except:
    print('Error') #if 'try' is incorrect(in code). program will print 'Error' 

try:
    print('Hello') #if 'try' is correct(in code). program will print 'Hello'
except:
    print('Error')

try:
    print('Hello')
except:
    print('Error')
else:
    print('No Error')