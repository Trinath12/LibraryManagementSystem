import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview

from GUIMain import *

try:
    connection = mysql.connector.connect(user='root',password='123456789',host='localhost',db='LIBRARY')
except Error as e:
    print(e)
    
present_date = datetime.today()

frame3 = Toplevel()
frame3.title("Fine")

def show_fines():
    borrower_id = borrowerEntry.get()
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT Card_no FROM BORROWER WHERE BORROWER.Card_no = '" + str(borrower_id) + "')")
    result = cursor.fetchall()
    total_fine = 0
    
    if result == [(0,)]:
        messagebox.showinfo("Error", "Borrower does not exist in data")
    else:
        cursor.execute("SELECT FINES.fine_amt, FINES.paid FROM FINES JOIN BOOK_LOANS ON FINES.Loan_Id = BOOK_LOANS.Loan_Id WHERE BOOK_LOANS.Card_no = '" + str(borrower_id) + "'")
        result = cursor.fetchall()
        total_fine = 0
        for elem in result:
            if elem[1] == 0:
                total_fine += float(elem[0])
    
    v.set("Fine: $ " + str(total_fine))

def pay_fine():
    borrower_id = borrowerEntry.get()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT EXISTS(SELECT Card_no FROM BORROWER WHERE BORROWER.Card_no = '" + str(borrower_id) + "')")
    result = cursor.fetchall()
    if result == [(0,)]:
        messagebox.showinfo("Error", "Borrower does not exist in data")
    else:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT FINES.Loan_Id FROM FINES JOIN BOOK_LOANS ON FINES.Loan_Id = BOOK_LOANS.Loan_Id WHERE BOOK_LOANS.Card_no = '" + str(
                borrower_id) + "'")
        result = cursor.fetchall()
        for i in result:
            cursor = connection.cursor()
            cursor.execute("UPDATE FINES SET FINES.paid = 1 WHERE FINES.Loan_Id = '" + str(i[0]) + "'")
            connection.commit()
        messagebox.showinfo("Success", "Fines Paid!")
        frame3.destroy()

v = StringVar()

borrowerLabel = Label(frame3, text="Input Borrower ID").grid(row=0, column=0)
borrowerEntry = Entry(frame3).grid(row=1, column=0)

showFineBtn = Button(frame3, text="Show Fines", command=show_fines).grid(row=2, column=0)
fineLabel = Label(frame3, textvariable=v).grid(row=3, column=0)
payFineBtn = Button(frame3, text="Pay Fine", command=pay_fine).grid(row=4, column=0)

