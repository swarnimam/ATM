import datetime
import numpy as np
import socket
import sqlite3
import json
import cv2
from random import choice
from PIL import Image as Img
from PIL import ImageTk
from keras.models import load_model
from keras_facenet import FaceNet
from tkinter import *
from tkinter import messagebox
from tkinter import ttk


class Application(Tk):

    def __init__(self):
        super().__init__()
        self.title("Welcome!")
        w = 235
        h = 170
        self['bg'] = 'blue'
        self.position_window(w, h)
        self.resizable(False, False)
        self.customer = StringVar()
        self.code_trial = 0
        self.pin_trial = 0
        self.customer_code = StringVar()
        self.pins = {'Customer code': 0}
        self.connect_socket()
        self.socket.send(str.encode('pin'))
        self.pins = json.loads(bytes.decode(self.socket.recv(1024)))
        Application.pins = self.pins
        self.socket.send(str.encode('names'))
        Application.names = json.loads(bytes.decode(self.socket.recv(1024)))
        self.socket.send(str.encode('acct'))
        Application.account_no = json.loads(bytes.decode(self.socket.recv(1024)))
        self.socket.send(str.encode('balance'))
        Application.balance = json.loads(bytes.decode(self.socket.recv(1024)))
        self.socket.send(str.encode('trxn'))
        Application.trxn_id = json.loads(bytes.decode(self.socket.recv(1024)))
        self.socket.send(str.encode('q'))
        self.grid()
        self.create_widgets()

    def connect_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 5424
        self.host = socket.gethostbyname("localhost")
        self.socket.connect((self.host, self.port))
        data = bytes.decode(self.socket.recv(1024))
        print(data)

    def position_window(self, w, h):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.resizable(False, False)

    def create_widgets(self):

        self.label_title = Label(self, text="Welcome to the Bank!", font=("Time New Romans", 13, "bold"), bg='white', fg='blue')
        self.label_title.grid(row=3, column=1, columnspan=5, pady=10, padx=25)
        cur_row = 3
        cur_row += 1
        self.label_logIn = Label(self, text="Sign in below: ", font="Calibri 10 normal", bg='white', fg='blue')
        self.label_logIn.grid(row=cur_row, column=2, columnspan=5, padx=20)
        cur_row += 1
        self.frame = Frame(self)
        self.label_customer_code = Label(self.frame, text="Customer code: ", font="Arial 10 normal", bg='white')
        self.label_customer_code.grid(row=0, column=1, sticky=W)
        self.entry_customer_code = Entry(self.frame, text=" ", textvariable=self.customer_code)
        self.entry_customer_code.grid(row=0, column=2, sticky=E)
        self.frame.grid(row=cur_row, column=3, columnspan=4, pady=10)
        cur_row += 1
        self.btn_sign_in = Button(self, text="Sign In ", font='Cambria 8 bold', width=12, command=self.sign_in, bg='black', fg='white')
        self.btn_sign_in.grid(row=cur_row, column=4)

    def customer_exist(self, customer_code):
        for i in self.pins:
            if customer_code == i:
                return i
        return None

    def contact_customer_service(self):
        messagebox.showinfo(title='Sorry!', message='Too many attempts, contact customer service')

    def wrong_code(self,value):
        messagebox.showinfo(title='Try Again!', message=f'You have entered the wrong {value}, try again')

    def wrong_value(self, value):
        messagebox.showinfo(title='Try Again!', message=f'{value} must be number digits only, try again')

    def code_length(self, value):
        messagebox.showinfo(title='Try Again!', message=f'{value} must be exactly 4 digits long, try again')

    def check_int(self, value):
        try:
            return int(value)
        except ValueError as Argument:
            print("Value must be numbers only\n", Argument)

    def check_len(self, value):
        if len(value) == 4:
            return True
        else:
            return False

    def sign_in(self):
        customer_code = self.customer_code.get()

        if self.check_len(customer_code):
            if type(self.check_int(customer_code)) == int:
                Application.customer = self.customer_exist(customer_code)
                if Application.customer:
                    self.destroy()
                    VerificationWindow()
                else:
                    self.entry_customer_code.delete(0, END)
                    self.wrong_code('Customer code')
                    self.code_trial += 1
                    print(f'Trial ={self.code_trial}')
            else:
                self.entry_customer_code.delete(0, END)
                self.wrong_value('Customer code')
                self.code_trial += 1
                print(f'Trial ={self.code_trial}')
        else:
            self.code_length('Customer code')
            self.code_trial += 1
            print(f'Trial ={self.code_trial}')
        if self.code_trial == 3:
            self.contact_customer_service()
            self.destroy()


class VerificationWindow(Tk):

    embedder=FaceNet();
    model=load_model('data/atm_model.h5');

    def __init__(self):
        super().__init__()
        self.title("Verification!")
        w=645
        h=550
        self['bg']='blue'
        Application.position_window(self, w, h)
        self.protocol('WM_DELETE_WINDOW', self.destructor)
        self.customer = Application.customer
        self.code_trial=0
        VerificationWindow.customer=self.customer;
        VerificationWindow.name = Application.names[Application.customer].title()
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.grid()
        self.create_widgets()
        self.video_loop()
    
    def create_widgets(self):
        self.panel=Label(self)
        self.panel.grid(row=1,column=1)
        self.btn_login = Button(self, text="Capture Image!", font='Cambria 12 bold', width=12, command=self.verify, bg='black', fg='white')
        self.btn_login.grid(row=2, column=1)

    def destructor(self):
        self.destroy()
        self.vs.release()
        cv2.destroyAllWindows()

    def video_loop(self):
        ok, frame = self.vs.read()
        if ok:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_image = Img.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)
        self.after(30, self.video_loop)

    def verify(self):
        pixels=np.asarray(self.current_image);
        detections=VerificationWindow.embedder.extract(pixels,threshold=0.95);
        if len(detections)==0:
            messagebox.showinfo(title='Attention!', message=f'No face detected, try again');
            return;
        else:
            if len(detections)>1:
                messagebox.showinfo(title='Attention!', message=f'Multiple faces detected, try again');
                self.code_trial+=1;
                print(f'Trial ={self.code_trial}')
                return;
            else:
                face_embedding=detections[0]['embedding'];
                data=np.expand_dims(face_embedding,axis=1);
                data=data.reshape(1,data.shape[0],data.shape[1]);
                y=VerificationWindow.model.predict(data);
                y=y.reshape(1);
                print(VerificationWindow.customer,round(y[0]));
                if int(VerificationWindow.customer)==round(y[0]):
                    print("Facial Verification Successful.");
                    self.destructor();
                    AuthenticateWindow();
                else:
                    print("Facial Verification Failed, Retry!")
                    self.code_trial+=1;
                    print(f'Trial ={self.code_trial}')
                    return;
            if self.code_trial==3:
                self.contact_customer_service()
                self.destroy()


class AuthenticateWindow(Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Authentication!")
        w = 250
        h = 170
        self['bg'] = 'blue'
        Application.position_window(self, w, h)
        self.customer = Application.customer
        self.pin_trial = 0
        AuthenticateWindow.name = Application.names[Application.customer].title()
        self.grid()
        self.create_widgets()

    def create_widgets(self):

        cur_row = 0
        self.pin_frame = Frame(self)
        f_row = 0
        self.label_welcome = Label(self.pin_frame, text=f"Welcome {AuthenticateWindow.name}", font="Calibri 12 normal", bg='white', fg='black')
        self.label_welcome.grid(row=f_row, column=1)
        f_row += 1
        self.label_sign_in = Label(self.pin_frame, text="Enter pin to continue: ", font="Calibri 10 normal", bg='white',fg='blue')
        self.label_sign_in.grid(row=f_row, column=1, pady=10)
        f_row += 1
        self.pin = StringVar()
        self.entry_pin = Entry(self.pin_frame, text=" ", textvariable=self.pin, show='*')
        self.entry_pin.grid(row=f_row, column=1, pady=10)
        self.pin_frame['bg'] = 'blue'
        self.pin_frame.grid(row=cur_row, column=3, padx=25, pady=10)
        cur_row += 1
        self.btn_login = Button(self, text="Log In ", font='Cambria 8 bold', width=12, command=self.enterapp, bg='black', fg='white')
        self.btn_login.grid(row=cur_row, column=3)

    def authenticate(self, customer, pin):
        if str(Application.pins[customer]) == str(pin):
            return True
        else:
            return False

    def enterapp(self):
        customer = self.customer
        pin = self.pin.get()

        if Application.check_len(self, pin):
            if type(Application.check_int(self, pin)) == int:
                if self.authenticate(customer, pin):
                    self.destroy()
                    print('login successful')
                    Transaction()
                else:
                    self.entry_pin.delete(0, END)
                    Application.wrong_code(self, 'Pin')
                    self.pin_trial += 1
                    print(f'trial ={self.pin_trial}')
            else:
                self.entry_pin.delete(0, END)
                Application.wrong_value(self, 'Pin')
                self.pin_trial += 1
                print(f'trial ={self.pin_trial}')
        else:
            Application.code_length(self, 'Pin')
            self.pin_trial += 1
            print(f'trial ={self.pin_trial}')
        if self.pin_trial == 3:
            Application.contact_customer_service(self)
            self.destroy()


class Transaction(Tk):

    w=310
    h=220
    bg='purple'

    def __init__(self):
        super().__init__()
        self.title("Transaction Screen")
        w = 250
        h = 250
        self['bg']='orange'
        Application.position_window(self, w, h)
        Transaction.balance = int(Application.balance[Application.customer])
        Transaction.acct_no = Application.account_no[Application.customer]
        self.grid()
        self.create_widgets()
        Transaction.wm_protocol(self, "WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        cur_row = 1
        self.t_frame = Frame(self)
        f_row = 0
        self.btn_balance = Button(self.t_frame, text="Check Balance", font='Cambria 8 bold', width=12, command=self.show_balance, bg='orange red', fg='white')
        self.btn_balance.grid(row=f_row, column=0, pady=15)
        f_row += 1
        self.btn_withdraw = Button(self.t_frame, text="Withdraw", font='Cambria 8 bold', width=12, command=self.withdrawScreen, bg='orange red', fg='white')
        self.btn_withdraw.grid(row=f_row, column=0, pady=15)
        f_row += 1
        self.btn_deposit = Button(self.t_frame, text="Deposit", font='Cambria 8 bold', width=12, command=self.depositScreen, bg='orange red', fg='white')
        self.btn_deposit.grid(row=f_row, column=0, pady=15)
        f_row += 1
        self.btn_transfer = Button(self.t_frame, text="Transfer", font='Cambria 8 bold', width=12, command=self.recipientScreen, bg='orange red', fg='white')
        self.btn_transfer.grid(row=f_row, column=0, pady=15)
        self.t_frame['bg'] = 'orange'
        self.t_frame.grid(row=cur_row, column=0, padx=80, pady=25)

    def show_balance(self):
        Transaction.withdraw(self)
        messagebox.showinfo(title='Account Balance', message='Dear {}\n Your current balance is Rs. {:,.2f}'.format(AuthenticateWindow.name, Transaction.balance))
        Transaction.deiconify(self)

    def withdrawScreen(self):
        Transaction.withdraw(self)
        withdraw_window = Toplevel(self)
        withdraw_window.title("Withdraw")
        withdraw_window['bg'] = self.bg
        Application.position_window(withdraw_window, self.w, self.h)
        withdraw_window.grab_set()
        self.withdraw_amount = StringVar()
        cur_row = 4
        withdraw_window.withdraw_frame = Frame(withdraw_window)
        withdraw_window.input_amount = Label(withdraw_window.withdraw_frame,text="How much would you like to withdraw?",font="Arial 10 normal", bg='white', fg='blue')
        withdraw_window.input_amount.grid(row=0, column=0)
        withdraw_window.label_withdraw_amount = Entry(withdraw_window.withdraw_frame, text=" ",textvariable=self.withdraw_amount)
        withdraw_window.label_withdraw_amount.grid(row=1, column=0, pady=10)
        withdraw_window.button_withdraw = Button(withdraw_window.withdraw_frame, text='Withdraw', font='Cambria 8 bold', width=12, command=self.withdrawl, bg='orange red', fg='white')
        withdraw_window.button_withdraw.grid(row=2, column=0, pady=5)
        withdraw_window.withdraw_frame['bg'] = 'purple'
        withdraw_window.withdraw_frame.grid(row=cur_row, column=3, rowspan=3, padx=40, pady=40)

    def depositScreen(self):
        Transaction.withdraw(self)
        deposit_window = Toplevel(self)
        deposit_window.title("Deposit")
        deposit_window['bg'] = self.bg
        Application.position_window(deposit_window, self.w, self.h)
        deposit_window.grab_set()
        self.deposit_amount = StringVar()
        cur_row = 4
        deposit_window.deposit_frame = Frame(deposit_window)
        deposit_window.input_amount = Label(deposit_window.deposit_frame,text="How much would you like to deposit?", font="Arial 10 normal", bg='white', fg='blue')
        deposit_window.input_amount.grid(row=0, column=0)
        deposit_window.label_deposit_amount = Entry(deposit_window.deposit_frame, text=" ", textvariable=self.deposit_amount)
        deposit_window.label_deposit_amount.grid(row=1, column=0, pady=10)
        deposit_window.button_deposit = Button(deposit_window.deposit_frame, text='Deposit', font='Cambria 8 bold', width=12, command=self.deposit, bg='orange red', fg='white')
        deposit_window.button_deposit.grid(row=2, column=0, pady=5)
        deposit_window.deposit_frame['bg'] = 'purple'
        deposit_window.deposit_frame.grid(row=cur_row, column=3, rowspan=3, padx=40, pady=40)

    def recipientScreen(self):
        Transaction.withdraw(self)
        recipient_window = Toplevel(self)
        recipient_window.title("Transfer to:")
        recipient_window['bg'] = self.bg
        Application.position_window(recipient_window, self.w, self.h)
        recipient_window.grab_set()
        self.bank = StringVar()
        self.banks = ['State Bank of India', 'Bank of India', 'ICICI Bank', 'Axis Bank', 'HDFC Bank', 'Union Bank of India', 'Punjab National Bank', 'Central Bank of India', 'Allahabad Bank', 'Kotak Bank']
        self.recipient = StringVar()
        cur_row = 0
        recipient_window.recv_frame = Frame(recipient_window)
        recipient_window.r_frame = Frame(recipient_window.recv_frame)
        recipient_window.label_recipient = Label(recipient_window.r_frame, text="Enter Recipient\nAccount Number:", font="Arial 10 normal", bg='white')
        recipient_window.label_recipient.grid(row=0, column=1, sticky=W)
        recipient_window.entry_recipient = Entry(recipient_window.r_frame, text=" ", textvariable=self.recipient)
        recipient_window.entry_recipient.grid(row=0, column=2, sticky=W, padx=5)
        recipient_window.label_recipient_bank = Label(recipient_window.r_frame, text="Select Recipient \nBank: ", font="Arial 10 normal", bg='white')
        recipient_window.label_recipient_bank.grid(row=1, column=1, sticky=W, pady=10)
        recipient_window.recipient_bank_box = ttk.Combobox(recipient_window.r_frame, values=self.banks, textvariable=self.bank, state='readonly')
        recipient_window.recipient_bank_box.grid(row=1, column=2, sticky=E, padx=5, pady=10)
        recipient_window.r_frame['bg'] = self.bg
        recipient_window.r_frame.grid(row=cur_row, column=0, pady=10)
        cur_row += 1
        recipient_window.button_transfer = Button(recipient_window.recv_frame, text='Submit', font='Cambria 8 bold', width=12, command=self.confirm_recv, bg='orange red', fg='white')
        recipient_window.button_transfer.grid(row=cur_row, column=0, pady=5)
        recipient_window.recv_frame['bg'] = 'purple'
        recipient_window.recv_frame.grid(row=cur_row, column=3, rowspan=3, padx=40, pady=40)

    def transferScreen(self):
        Transaction.withdraw(self)
        transfer_window = Toplevel(self)
        transfer_window.title("Transfer")
        transfer_window['bg'] = self.bg
        Application.position_window(transfer_window, self.w, self.h)
        transfer_window.grab_set()
        self.transfer_amount = StringVar()
        cur_row = 4
        transfer_window.transfer_frame = Frame(transfer_window)
        transfer_window.input_amount = Label(transfer_window.transfer_frame, text="How much would you like to transfer?", font="Arial 10 normal", bg='white', fg='blue')
        transfer_window.input_amount.grid(row=0, column=0)
        transfer_window.label_transfer_amount = Entry(transfer_window.transfer_frame, text=" ", textvariable=self.transfer_amount)
        transfer_window.label_transfer_amount.grid(row=1, column=0, pady=10)
        transfer_window.button_transfer = Button(transfer_window.transfer_frame, text='Transfer', font='Cambria 8 bold', width=12, command=self.transfer, bg='orange red', fg='white')
        transfer_window.button_transfer.grid(row=2, column=0, pady=5)
        transfer_window.transfer_frame['bg'] = 'purple'
        transfer_window.transfer_frame.grid(row=cur_row, column=3, rowspan=3, padx=40, pady=40)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def confirm(self):
        if messagebox.askyesno("Another transaction?", "Do you want to perform another transaction?"):
            self.destroy()
            AuthenticateWindow()
        else:
            self.destroy()

    def account_length(self):
        messagebox.showinfo(title='Try Again!', message='Account number must be exactly 10 digits long, try again')

    def empty_bank(self):
        messagebox.showinfo(title='Try Again!', message='Please select a customer bank and try again')

    def insufficient_bal(self):
        messagebox.showinfo(title='Insufficient Balance!', message='You do not have sufficient funds to complete this transaction')

    def withdrawl(self):
        withdraw_amount = self.withdraw_amount.get()
        if type(Application.check_int(self, withdraw_amount)) == int:
            if int(withdraw_amount) <= Transaction.balance:
                Transaction.balance -= int(withdraw_amount)
                Application.balance[Application.customer] = Transaction.balance
                transfer_date = datetime.datetime.now()
                date = str(transfer_date)
                amount = "-" + str(withdraw_amount)
                self.record_trxn(amount, date)
                self.updateSqliteTable()
                self.confirm()
            else:
                self.withdraw_amount.set("")
                self.insufficient_bal()
        else:
            self.withdraw_amount.set("")
            Application.wrong_value(self, 'Amount')

    def deposit(self):
        deposit_amount = self.deposit_amount.get()
        if type(Application.check_int(self, deposit_amount)) == int:
            Transaction.balance += int(deposit_amount)
            Application.balance[Application.customer] = Transaction.balance
            transfer_date = datetime.datetime.now()
            date = str(transfer_date)
            amount = "+" + str(deposit_amount)
            self.record_trxn(amount, date)
            self.updateSqliteTable()
            self.confirm()
        else:
            self.deposit_amount.set("")
            Application.wrong_value(self, 'Amount')

    def confirm_recv(self):
        recipient_acct = self.recipient.get()
        if type(Application.check_int(self, recipient_acct)) == int:
            if len(recipient_acct) == 10:
                bank = self.bank.get()
                if len(bank) == 0:
                    self.empty_bank()
                else:
                    self.transferScreen()
            else:
                self.recipient.set("")
                self.account_length()
        else:
            self.recipient.set("")
            Application.wrong_value(self, 'Account number')

    def transfer(self):
        transfer_amount = self.transfer_amount.get()
        if type(Application.check_int(self, transfer_amount)) == int:
            if int(transfer_amount) <= Transaction.balance:
                Transaction.balance -= int(transfer_amount)
                Application.balance[Application.customer] = Transaction.balance
                transfer_date = datetime.datetime.now()
                date = str(transfer_date)
                amount = "-" + str(transfer_amount)
                self.record_trxn(amount, date)
                self.updateSqliteTable()
                self.confirm()
            else:
                self.transfer_amount.set("")
                self.insufficient_bal()
        else:
            self.transfer_amount.set("")
            Application.wrong_value(self, 'Amount')

    def record_trxn(self, amount, date):
        try:
            con = sqlite3.connect('data/atm.db')
            cursor = con.cursor()
            print("Connected to SQLite")
            sequence = [i for i in range(1000, 5000)]
            trxn_IDs = [x for x in sequence if x not in Application.trxn_id]
            trxn_id = str(choice(trxn_IDs))
            Application.trxn_id.append(int(trxn_id))
            acct_no = str(Transaction.acct_no)
            balance = str(Transaction.balance)
            stmt = "INSERT INTO Trxn(trxn_id, accountNo, amount, working_bal, trxn_date) VALUES(?, ?, ?, ?, ?)"
            values = [(trxn_id, acct_no, amount, balance, date)]
            cursor.executemany(stmt, values)
            con.commit()
            print("Record Updated successfully")
            cursor.close()
        except sqlite3.Error as error:
            print("Failed to update SQLite table", error)
        finally:
            if con:
                con.close()
                print("The SQLite connection is closed")

    def updateSqliteTable(self):
        try:
            conn = sqlite3.connect('data/atm.db')
            cursor = conn.cursor()
            print("Connected to SQLite")
            sql_update_query = f"""UPDATE Customers SET account_balance = {Transaction.balance} WHERE customer_code = {Application.customer}"""
            cursor.execute(sql_update_query)
            conn.commit()
            print("Record Updated successfully ")
            cursor.close()
        except sqlite3.Error as error:
            print("Failed to update SQLite table", error)
        finally:
            if conn:
                conn.close()
                print("The SQLite connection is closed")


if __name__ == "__main__":
    app = Application();
    app.mainloop();