'''
#Create table sqlite
import sqlite3
conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()
c.execute("""CREATE TABLE user(id integer PRIMARY KEY AUTOINCREMENT,
 fname varchar(30) NOT NULL,
 lname varchar(30) NOT NULL,
 email varchar(100) NOT NULL)""")
conn.commit()
conn.close()

#Import info
import sqlite3
conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()
c.execute("""INSERT INTO user(id,fname,lname,email) VALUES(NULL,"Kittisak","Janmahong","kittiksak.j@kkumail.com")""")
c.execute("""INSERT INTO user VALUES(NULL,"Kittikawin","Chanbuttarach","kittikawin.c@kkumail.com")""")
conn.commit()
conn.close()

#Add info
import sqlite3

def insertTrousers(fname,lname,email):
    try:
        conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
        c = conn.cursor()

        sql = """INSERT INTO user(fname,lname,email) VALUES(?,?,?)"""
        data = (fname,lname,email)
        c.execute(sql,data)
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print('failed to insert')
    finally:
        if conn:
            conn.close()

insertTrousers('Peter','Jackson','peter.j@kkumail.com')

#Insertion info
data = ('a','a','a')
c.execute("INSERT INTO user(fname,lname,email) VALUES(?,?,?)",data)

#Add many record
import sqlite3

conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()
try:  
 data = [("Teerepat","Phoudom","teerapat.p@kkumail.com"),("Purachet","Chanmee","purachet.c@kkumail.com"),("Natdanai","Sirawanich","natdanai.s@kkumail.com")]
 c.executemany("INSERT INTO user(fname,lname,email) VALUES(?,?,?)",data)
 conn.commit()
 conn.close()

except sqlite3.Error as e:
 print('failed to insert')
finally:
 if conn:
     conn.close()

#Select one data
import sqlite3

conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()

c.execute("""SELECT fname,lname FROM user""") #use (*) to shoe all collumn
result = c.fetchone()
print(result)

#Select all data
import sqlite3

conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()

c.execute("""SELECT fname,lname FROM user""")
result = c.fetchall()
for x in result:
    print(x)

#Data append
import sqlite3

def insertTrousers(fname,lname,email):
    try:
        conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
        c = conn.cursor()

        sql = """INSERT INTO user(fname,lname,email) VALUES(?,?,?)"""
        data = (fname,lname,email)
        c.execute(sql,data)
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print('failed to insert')
    finally:
        if conn:
            conn.close()

def add(fname,lname,email):
    connlist.append(fname)
    connlist.append(lname)
    connlist.append(email)
    insertTrousers(fname,lname,email)
    return fname,lname,email

connlist = []
f = str(input('Insert your first name :'))
l = str(input('Insert your last name :'))
em = str(input('Insert your email :'))
add(f,l,em)

#WHERE function
import sqlite3

conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()

c.execute("""SELECT * FROM user WHERE fname = "Kittisak" """) #use (*) to shoe all collumn
result = c.fetchall()
for x in result:
    print(x)

#Limit data
import sqlite3

conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()

c.execute("""SELECT fname,lname FROM user LIMIT 3""")
result = c.fetchall()
for x in result:
    print(x)

#Insert tuple info
import sqlite3

conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()

name = ('Kittisak',)
c.execute("""SELECT * FROM user WHERE fname = ? """,name)
result = c.fetchall()
for x in result:
    print(x)

#List counting function (MAX > MIN)
import sqlite3

conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()

try :
    c.execute("""SELECT * FROM user ORDER BY id DESC""")
    conn.commit()
    result = c.fetchall()
    for x in result:
        print(x)
    c.close()

except sqlite3.Error as e:
     print('failed to insert')
finally:
     if conn:
         conn.close()

#OFFSET function
import sqlite3

conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()

try :
    c.execute("""SELECT * FROM user LIMIT 5 OFFSET 2""")
    result = c.fetchall()
    for x in result:
        print(x)
    c.close()

except sqlite3.Error as e:
     print('failed to insert')
finally:
     if conn:
         conn.close()

#DELETE function
import sqlite3

conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()

try :
    c.execute("""DELETE FROM user WHERE id = 1""") #if want to dalete all data typp 'DELETE FROM user'
    result = c.fetchall()
    for x in result:
        print(x)
    c.close()

except sqlite3.Error as e:
     print('failed to insert')
finally:
     if conn:
         conn.close()
'''
#UPDATE function
import sqlite3

conn = sqlite3.connect (r"C:\Python_Kittikawin\example.db\example.db")
c = conn.cursor()

try :
    data = ('Apsorn','Maneejam','apsorn.m@kkumail.com','3')
    c.execute("""UPDATE user SET fname = ? , lname = ? , email = ? WHERE id = ?""",data) 
    conn.commit()
    c.close()

except sqlite3.Error as e:
     print('failed to insert')
finally:
     if conn:
         conn.close()