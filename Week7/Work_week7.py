'''
#excercise 1
def my(names,lnames,id,address):
    print('Hello, i am',names,lnames)
    print('My student ID is',id)
    print('I come from',address)

def line():
    print('---------------------')

names = str(input('What is your name ?:'))
lnames = str(input('What is your last name ?:'))
id = int(input('What is your student ID ?:'))
address = str(input('Where you come from ?:'))

line()
my(names,lnames,id,address)
line()

#excercise 2
def input_data():
    names = str(input('What is your name ?:'))
    lnames = str(input('What is your last name ?:'))
    id = int(input('What is your student ID ?:'))
    address = str(input('Where you come from ?:'))
    return names,lnames,id,address

def my():
    names,lnames,id,address = input_data()
    line()
    print('Hello, i am',names,lnames,id,'from',address)

def line():
    print('---------------------')

line()
my()
line()
'''
#excercise 3
worddic = []
tagdic = []
meandic = []
alldic = [worddic,tagdic,meandic]
def addw():
    w = input('Add your word :')
    worddic.append(w)
    t = input("What's kind of word do you want to add ? (n, v, adj, adv):")
    if t == 'n':
        t = 'n. noun'
        tagdic.append(t)
    elif t == 'v':
        t = 'v. verb'
        tagdic.append(t)
    elif t == 'adj':
        t = 'adj. adjective'
        tagdic.append(t)
    elif t == 'adv':
        t = 'adv. adverb'
        tagdic.append(t)
    else:
        print("Don't have this type")
        return addw()
    m = input('What is the meaning of this word ?:')
    meandic.append(m)
    line()
    print('SAVED')

def showw():
    line()
    print('All words =\m',len(worddic))
    line()
    print(f'{'Vocabulary':<15}{'Tag':<15}{'Meaning':<15}')
    for a in range(len(worddic)):
     print(f'{alldic[0][a]:<15}{alldic[1][a]:<15}{alldic[2][a]:<15}')

def removew():
   r = input('What is the word you want to delete ?:')
   if r in worddic:
      c = input('Do you want to delete this word [y/n]:')
      if c == 'y':
         id = worddic.index(r)
         worddic.pop(id)
         tagdic.pop(id)
         meandic.pop(id)
         line()
         print('word',r,'deleted')
      else:
         line()
         print('cancle')

def line():
    print('-----------------------------')

def menu():
     while(True):
         print('Dictionary program')
         line()
         print('[1] add word\n [2] show Dictionary\n [3] delete word\n [4] close program')
         m = input('Choose your program:')
         if m == '1':
             addw()
         elif m == '2':
             showw()
         elif m == '3':
             removew()
         else:
             x = input('Do you want to close the program ? [y/n]:') 
             if x == 'y':
                 break
             else:
                 return
menu()
            