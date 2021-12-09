import sqlite3

conn = sqlite3.connect('data/atm.db')
cursor = conn.cursor()

stmt = """CREATE TABLE Customers(customer_code INTEGER(4) PRIMARY KEY, 
						        account_name VARCHAR(30), 
						        account_type VARCHAR(10), 
						        account_balance VARCHAR(50), 
						        accountNo INTEGER(10), 
						        pin INTEGER(4))"""
cursor.execute(stmt)
stmt = "INSERT INTO Customers(customer_code, account_name, account_type, account_balance, accountNo, pin) VALUES(?, ?, ?, ?, ?, ?)"
values = [(1021, 'Kumar Swarnimam', 'Savings', 100000, 1234567890, 1111), 
            (1022, 'Kumar Swapnil', 'Savings', 500000, 1234567891, 2222),
            (1023, 'Shah Rukh Khan', 'Current', 2500000, 1234567892, 3333)]
cursor.executemany(stmt, values)

stmt = """CREATE TABLE Trxn(trxn_id INTEGER(4) PRIMARY KEY, 
                            accountNo INTEGER(10), 
                            amount VARCHAR(50), 
                            working_bal INTEGER(50), 
                            trxn_date DATETIME(70))"""
cursor.execute(stmt)

conn.commit()
conn.close()