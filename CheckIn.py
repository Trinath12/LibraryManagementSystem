import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Treeview

from GUIMain import *
try:
    connection = mysql.connector.connect(user='root',password='123456789',host='localhost',db='LIBRARY')
except Error as e:
    print(e)

frame1 = Toplevel()
frame1.title("Check In Here")



bookForCheckInID,search_string, data = None, None, None


def find_bookloans():
    search_string = searchBox.get()
    cursor = connection.cursor()
    cursor.execute("select BOOK_LOANS.Loan_Id, BOOK_LOANS.ISBN, BOOK_LOANS.Card_no, BOOK.title, BOOK_LOANS.Date_in from BOOK_LOANS "
                   "join BORROWER on BOOK_LOANS.Card_no = BORROWER.Card_no "
                   "join BOOK on BOOK_LOANS.ISBN = BOOK.ISBN "
                   "where BOOK_LOANS.ISBN like concat('%', '" + search_string + "', '%') or "
                    "BORROWER.Bname like concat('%', '" + search_string + "', '%') or "
                    "BOOK_LOANS.Card_no like concat('%', '" + search_string + "', '%')")

    data = cursor.fetchall()
    view_data(data)

def view_data(data):
    table.delete(*table.get_children())
    for i in data:
        if i[4] is None:
            table.insert('', 'end', text=str(i[0]), values=(i[1], i[2], i[3]))

def select_book_for_checkin(a):
    global bookForCheckInID
    curItem = table.focus()
    bookForCheckInID = table.item(curItem)['text']

def check_in():
    global bookForCheckInID, present_date

    if bookForCheckInID is None:
        messagebox.showinfo("Warn!", "Press on Book to CheckIn")
        return None
    cursor = connection.cursor()
    cursor.execute("SELECT BOOK_LOANS.Date_in FROM BOOK_LOANS WHERE BOOK_LOANS.Loan_Id = '" + str(bookForCheckInID) + "'")
    result = cursor.fetchall()
    if result[0][0] is None:
        cursor.execute("UPDATE BOOK_LOANS SET BOOK_LOANS.Date_in = '" + str(present_date) + "' WHERE BOOK_LOANS.Loan_Id = '"
                       + str(bookForCheckInID) + "'")
        connection.commit()
        messagebox.showinfo("Success", "Book Checked In")
        frame1.destroy()
    else:
        messagebox.showinfo("Failed", "Try again")
        return None




searchLabel = Label( text="Search here: Borrower ID, Borrower Name or ISBN").grid(row=0, column=0, padx=20, pady=20)

searchBox = Entry().grid(row=1, column=0)

searchBtn = Button(frame1, text="Search", command=find_bookloans).grid(row=2, column=0)

table = Treeview(frame1, columns=["Loan ID", "ISBN", "Borrower ID", "Title"])
table.grid(row=3, column=0)
table.heading('#0', text="Loan ID")
table.heading('#1', text="ISBN")
table.heading('#2', text="Borrower ID")
table.heading('#3', text="Book Title")
table.bind('<ButtonRelease-1>', select_book_for_checkin)

checkInBtn = Button(frame1, text="Check In", command=check_in).grid(row=4, column=0)


