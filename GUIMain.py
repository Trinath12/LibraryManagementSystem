import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview

global connection,present_date,bookForCheckOutIsbn

present_date = datetime.today()

from CheckIn import *
from AddBorrowers import *
from PayFines import *

try:
    connection = mysql.connector.connect(user='root',password='123456789',host='localhost',db='LIBRARY')
except Error as e:
    print(e)


def search():
    search_string = SearchBox.get()
    cursor = connection.cursor()
    cursor.execute("select BOOK.isbn, BOOK.title, AUTHORS.AuthorName from BOOK join BOOK_AUTHORS on "
                        "BOOK.isbn = BOOK_AUTHORS.isbn join AUTHORS on BOOK_AUTHORS.author_id = AUTHORS.author_id "
                        "where BOOK.title like concat('%', '" + search_string + "', '%') or "
                        "AUTHORS.AuthorName like concat('%', '" + search_string + "', '%') or "
                        "BOOK.isbn like concat('%', '" + search_string + "', '%')")

    data = cursor.fetchall()
    view_data(data)
    
def view_data(data):
    ResultTreeview.delete(*ResultTreeview.get_children())
    for i in data:
        cursor = connection.cursor()
        cursor.execute("SELECT EXISTS(SELECT BOOK_LOANS.isbn from BOOK_LOANS where BOOK_LOANS.isbn = '" + str(i[0]) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            availability = "Available"
        else:
            cursor = connection.cursor()
            cursor.execute("SELECT BOOK_LOANS.Date_in from BOOK_LOANS where BOOK_LOANS.isbn = '" + str(i[0]) + "'")
            r = cursor.fetchall()
            if r[-1][0] is None:
                availability = "Not Available"
            else:
                availability = "Available"
        ResultTreeview.insert('', 'end', text=str(i[0]),
                                   values=(i[1], i[2], availability))
def selectBookForCheckout(a):
    global bookForCheckOutIsbn
    current_book = ResultTreeview.focus()
    bookForCheckOutIsbn = ResultTreeview.item(current_book)['text']
    
def check_out():
    global bookForCheckOutIsbn

    if bookForCheckOutIsbn is None:
        messagebox.showinfo("Error","Please Select Book!!!")
        return None
    borrowerId = simpledialog.askstring("Check Out Book", "Enter Borrower ID")
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT Card_no from BORROWER WHERE BORROWER.Card_no = '" + str(borrowerId) + "')")
    result = cursor.fetchall()

    if result == [(0,)]:
        messagebox.showinfo("Warn", "Borrower doesn't exist in database")
        return None
    else:
        count = 0
        cursor = connection.cursor()
        cursor.execute("SELECT BOOK_LOANS.Date_in from BOOK_LOANS WHERE BOOK_LOANS.Card_no = '" + str(borrowerId) + "'")
        result = cursor.fetchall()
        for i in result:
            if i[0] is None:
                count += 1
        if count >= 3:
            messagebox.showinfo("Limit exceeded", "Borrower has loaned 3 books already!")
            return None
        else:
            cursor = connection.cursor()
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            cursor.execute("INSERT INTO BOOK_LOANS (ISBN, Card_no, Date_out, Due_date) VALUES ('" + bookForCheckOutIsbn + "', '" + borrowerId + "', '" + str(present_date) + "', '" + str(present_date + timedelta(days=14)) + "')")
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            connection.commit()
            cursor = connection.cursor()
            cursor.execute("SELECT MAX(Loan_Id) FROM BOOK_LOANS")
            r = cursor.fetchall()
            loan_id = r[0][0]
            cursor.execute("INSERT INTO FINES (Loan_Id, fine_amt, paid) VALUES ('" + str(loan_id) + "', '0.00', '0')")
            connection.commit()
            messagebox.showinfo("Success", "Book Checked Out!")

def check_in():
    execfile('CheckIn.py')

def update_fines():
    cursor = connection.cursor()
    cursor.execute("SELECT BOOK_LOANS.Loan_Id, BOOK_LOANS.Date_in, BOOK_LOANS.Due_date FROM BOOK_LOANS")
    result = cursor.fetchall()

    for record in result:
        date_in, date_due = record[1], record[2]
        if date_in is None:
            date_in = present_date.date()
    
        difference = date_in - date_due
        if difference.days > 0:
            fine = int(difference.days) * 0.25
        else:
            fine = 0
        cursor = connection.cursor()
        cursor.execute("UPDATE FINES SET FINES.fine_amt = '" + str(fine) + "' WHERE FINES.Loan_Id = '" + str(record[0]) + "'")
        connection.commit()
    messagebox.showinfo("Success", "Fines updated...")

def pay_fines():
    execfile('PayFines.py')

def add_borrower():
    execfile('AddBorrowers.py')    
    
def change_date():
    global present_date
    daysno = simpledialog.askstring("Change date(To Calculate fines)", "Enter no of days to extend:")
    present_date = present_date + timedelta(days=int(daysno))
    print(present_date)


# Main frame design
root=Tk()
frame = Frame(root, width=1000, height=1000)
frame.grid(row=10, column=10)
frame.grid_propagate(False)

        
     
SearchBox = Entry(frame, width=70)
SearchBox.grid(row=1, column=0)
   
SearchButton = Button(frame, text='Search', command=search).grid(row=2, column=0)


ActiveArea = Frame(frame).grid(row=5, column=0, sticky=N)

ResultTreeview = Treeview(ActiveArea, columns=["ISBN", "Book Name", "Author Name", "Availability"])
ResultTreeview.grid(row=60, column=5)
ResultTreeview.heading('#0', text="ISBN")
ResultTreeview.heading('#1', text="Book Name")
ResultTreeview.heading('#2', text="Author Name")
ResultTreeview.heading('#3', text="Availability")
ResultTreeview.bind('<ButtonRelease-1>', selectBookForCheckout)

checkOutBtn = Button(frame, text="Check Out Book", command=check_out).grid(row=30, column=0)

checkInBtn = Button(frame, text="Check In Book", command=check_in).grid(row=35, column=0)

updateFinesBtn = Button(frame, text="Updates Fines", command=update_fines).grid(row=40, column=0)

payFinesBtn = Button(frame, text="Pay Fines", command=pay_fines).grid(row=45, column=0)

changeDateBtn = Button(frame, text="Change Day", command=change_date).grid(row=50, column=0)

addBorrowerBtn = Button(frame, text="Add New Borrower", command=add_borrower).grid(row=55, column=0)

#frame.pack()
root.mainloop()