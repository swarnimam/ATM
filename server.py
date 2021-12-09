import socket
import sqlite3
import json

conn = sqlite3.connect("data/atm.db");
cursor = conn.cursor();

trxn_id = [];
names = {};
account_balance = {};
account_no = {};
pins = {};

for t in cursor.execute('SELECT * FROM Trxn'):
    trxn_id.append(t[0]);
for x in cursor.execute('SELECT * FROM Customers'):
    names[x[0]] = x[1];
    account_balance[x[0]] = x[3];
    account_no[x[0]] = x[4];
    pins[x[0]] = x[5];

cursor.close();
conn.close();

packaged_trxn = str.encode(json.dumps(trxn_id));
packaged_names = str.encode(json.dumps(names));
packaged_balance = str.encode(json.dumps(account_balance));
packaged_accountNo = str.encode(json.dumps(account_no));
packaged_pins = str.encode(json.dumps(pins));

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
host = '';
port = 5424;
server.bind((host, port));
server.listen();

while True:
    print(f'Server started, running on port {port}');
    client, addr = server.accept();
    client.send(str.encode(f'Accepted connection from {addr}'));
    while True:
        request = bytes.decode(client.recv(1024)).lower();
        if request == 'pin':
            client.send(packaged_pins);
        elif request == 'balance':
            client.send(packaged_balance);
        elif request == 'names':
            client.send(packaged_names);
        elif request == 'acct':
            client.send(packaged_accountNo);
        elif request == 'trxn':
            client.send(packaged_trxn);
        elif request == 'q':
            print(f'Disconnecting from {addr}');
            break;
        else:
            print('Invalid Request');
            print(f'Disconnecting from {addr}');
            break
    if input('Enter q to stop').upper() == 'Q':
        break;