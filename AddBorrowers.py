import mysql.connector
from mysql.connector import Error
from tkinter import *
from tkinter import messagebox

from GUIMain import *

try:
    connection = mysql.connector.connect(user='root',password='123456789',host='localhost',db='LIBRARY')
except Error as e:
    print(e)
    
frame2 = Toplevel()
frame2.title("Borrowing Person New")

def add_borrower():
    ssn = ssnTB.get()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(Card_no) from BORROWER")
    new_card_no = cursor.fetchall()[0][0]
    new_card_no=int(new_card_no[3:])+1
    new_card_no=str('ID00'+str(new_card_no))
    cursor.execute("SELECT EXISTS(SELECT Ssn FROM borrower WHERE borrower.ssn = '" + str(ssn) + "')")
    result = cursor.fetchall()
    if result == [(0,)]:
        address = ', '.join([addressTB.get(), cityTB.get(), stateTB.get()])
    
        cursor.execute("Insert into borrower (Card_no, ssn, bname, address, phone) Values ('" + new_card_no + "', '" + ssn + "', '" + str(nameTB.get()) + "', '" + str(address) + "', '" + str(numberTB.get()) + "')")
        connection.commit()
        frame2.destroy()
    else:
        messagebox.showinfo("Warn", "Borrower Already Exists!")


titleLabel = Label(frame2, text="Enter Details").grid(row=0, column=0)

nameLabel = Label(frame2, text="Full Name").grid(row=1, column=0)
nameTB = Entry(frame2).grid(row=2, column=0)

ssnLabel = Label(frame2, text="SSN").grid(row=5, column=0)
ssnTB = Entry(frame2).grid(row=6, column=0)

addressLabel = Label(frame2, text="Street").grid(row=7, column=0)
addressTB = Entry(frame2).grid(row=8, column=0)

cityLabel = Label(frame2, text="City").grid(row=9, column=0)
cityTB = Entry(frame2).grid(row=10, column=0)

stateLabel = Label(frame2, text="State").grid(row=11, column=0)
stateTB = Entry(frame2).grid(row=12, column=0)

numberLabel = Label(frame2, text="Phone Number").grid(row=13, column=0)
numberTB = Entry(frame2).grid(row=14, column=0)

addBtn = Button(frame2, text="Add", command=add_borrower).grid(row=15, column=0)

