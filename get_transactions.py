import sqlite3

conn = sqlite3.connect('data/atm.db')
cursor = conn.cursor()
stmt = "SELECT * FROM Trxn"
x=cursor.execute(stmt)
for i in x:
    print(i)
conn.commit()
conn.close()