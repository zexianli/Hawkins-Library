from flask import Flask
from flask import render_template, url_for
from flask import request, redirect
from flask import flash
from forms import memberLookUpForm, authorAddForm
from db_connector import connect_to_database, execute_query
import re
from datetime import datetime, date, timedelta


app = Flask(__name__)
app.config['SECRET_KEY'] = '123456789'



@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")

'''
Entity: Members 
'''
#--------------------------------------------------------
# Member Routing

'''
Functionality: SELECT
'''
@app.route("/member/lookUp", methods=['GET', 'POST'])
def memberLookup():
    
    print("Fetching and rendering look up member page.")
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT member_ID, first_name, last_name, address, email from members'
        result = execute_query(db_connection, query).fetchall()     
        print(result)
        
        return render_template("/member/lookUp.html", rows=result)
    
    # Searching for member
    elif request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        query = 'SELECT member_ID, first_name, last_name, address, email from members where first_name = %s AND last_name = %s'
        data = (fname, lname)
        search_result = execute_query(db_connection, query, data).fetchall()

        # If no such member exists, show message  
        if search_result == ():
            query = 'SELECT member_ID, first_name, last_name, address, email from members'
            result = execute_query(db_connection, query).fetchall()
            message = "No such member found."

            return render_template("/member/lookUp.html", rows=result, query_message=message)      

        # Otherwise, display member
        return render_template("/member/lookUp.html", rows=search_result)

'''
Functionality: INSERT
'''
@app.route("/member/add", methods=['GET', 'POST'])
def memberAdd():

    print("Fetching and rendering add member page.")
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT member_ID, first_name, last_name, address, email from members'
        result = execute_query(db_connection, query).fetchall()     
        print(result)
        
        return render_template("/member/add.html", rows=result)

    # Adding member
    elif request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        address = request.form['address']
        email = request.form['email'] 
        # If no email is provided, change email to NULL (None in Python)
        if email == '': 
            email = None
        query = 'INSERT INTO members (first_name, last_name, address, email) VALUES (%s, %s, %s, %s)' 
        data = (fname, lname, address, email)
        execute_query(db_connection, query, data).fetchall()        

        # Display results
        query = 'SELECT member_ID, first_name, last_name, address, email from members'
        add_result = execute_query(db_connection, query).fetchall()
        message = "Member added."
        
        return render_template("/member/add.html", rows=add_result, query_message=message)

'''
Functionality: DELETE
'''
@app.route("/member/remove", methods=['GET', 'POST'])
def memberRemove():

    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT * FROM members'
        result = execute_query(db_connection, query)
        return render_template("/member/remove.html", rows=result)
    
    # Finding and deleting member
    elif request.method == 'POST':
        memberID = request.form['memberID']
        fname = request.form['fname']
        lname = request.form['lname']

        # Doing test query in order to see if member exists
        test_query = 'SELECT member_ID, first_name, last_name, address, email from members WHERE member_ID = %s AND first_name = %s AND last_name = %s'
        test_data = ([memberID], fname, lname)
        test_result = execute_query(db_connection, test_query, test_data).fetchone()
        print(test_result)

        # If no such member exists, show message  
        if test_result == None:
            query = 'SELECT member_ID, first_name, last_name, address, email from members'
            result = execute_query(db_connection, query).fetchall()
            message = "No such member found."

            return render_template("/member/remove.html", rows=result, query_message=message)
        
        # Deleting member
        query = 'DELETE FROM members WHERE member_ID = %s and first_name = %s and last_name = %s'
        data = ([memberID], fname, lname)
        execute_query(db_connection, query, data)

        # Query to display new data from tables
        query = 'SELECT * FROM members'
        result = execute_query(db_connection, query)
        message = "Member removed."

        return render_template("/member/remove.html", rows=result, query_message=message)

'''
Functionality: UPDATE (part 1)
'''
@app.route("/member/update", methods=['GET', 'POST'])
def memberUpdate():
    
    print("Fetching and rendering select member to update page.")
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT member_ID, first_name, last_name, address, email from members'
        result = execute_query(db_connection, query).fetchall()     
        print(result)
        
        return render_template("/member/update.html", rows=result)
    
    # Finding member to be updated
    elif request.method == 'POST':
        memberID = request.form['memberID']
        query = 'SELECT member_ID, first_name, last_name, address, email from members WHERE member_ID = %s'
        data = ([memberID])
        member_result = execute_query(db_connection, query, data).fetchone()
        print(member_result)

        # If no such member exists, show message  
        if member_result == None:
            query = 'SELECT member_ID, first_name, last_name, address, email from members'
            result = execute_query(db_connection, query).fetchall()
            message = "No such member found."

            return render_template("/member/update.html", rows=result, query_message=message)

        # Otherwise, render pre-populated upate form
        return render_template("/member/updateForm.html", member=member_result)

'''
Functionality: UPDATE (part 2)
'''
@app.route("/member/updateForm", methods=['POST'])
def updateForm():

    print("Fetching and rendering update member results page.")
    db_connection = connect_to_database()

    # Get updates values from form
    if request.method == 'POST':
        memberID = request.form['memberID']
        fname = request.form['fname']
        lname = request.form['lname']
        address = request.form['address']
        email = request.form['email'] 
        # If no email is provided, change email to NULL (None in Python)
        if email == '': 
            email = None

        # Update member
        query = 'UPDATE members SET first_name = %s, last_name = %s, address = %s, email = %s WHERE member_ID = %s' 
        data = (fname, lname, address, email, [memberID])
        update_result = execute_query(db_connection, query, data)

        # Display updated result
        query = 'SELECT member_ID, first_name, last_name, address, email from members WHERE member_ID = %s'
        data = ([memberID])
        updated_member = execute_query(db_connection, query, data)  

        # Display all records
        query = 'SELECT member_ID, first_name, last_name, address, email from members'
        result = execute_query(db_connection, query).fetchall() 
        
        return render_template("/member/updateResult.html", updatedRows=updated_member, allRows=result)
#--------------------------------------------------------


'''
Entity: Checked_Out_Books
'''
#--------------------------------------------------------
# Checked_Out_Books Routing

'''
Functionality: SELECT
'''
@app.route("/transaction/lookUp", methods=['GET', 'POST'])
def transactionLookUp():
    
    print("Fetching and rendering look up transaction page.")
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
        result = execute_query(db_connection, query).fetchall()
        print(result)
        
        return render_template("/transaction/lookUp.html", rows=result)
    
    # Searching for transaction
    elif request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']

        # Find transactions by member's first and last name
        query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN WHERE members.first_name = %s AND members.last_name = %s'
        data = (fname, lname)
        search_result = execute_query(db_connection, query, data).fetchall()

        # If no such transaction exists, show message  
        if search_result == ():
            query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
            result = execute_query(db_connection, query).fetchall()
            message = "No such transaction found."
            return render_template("/transaction/lookUp.html", rows=result, query_message=message) 

        return render_template("/transaction/lookUp.html", rows=search_result)

'''
Functionality: INSERT
Relationship: NULLable 1:M relationship between Checked_Out_Books and Employees
'''
@app.route("/transaction/checkOut", methods=['GET', 'POST'])
def transactionCheckOut():
    
    print("Fetching and rendering check out book page.")
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
        result = execute_query(db_connection, query).fetchall()     
        print(result)
        
        return render_template("/transaction/checkOut.html", rows=result)

    # Adding transaction
    elif request.method == 'POST':
        memberID = request.form['memberID']
        isbn = request.form['isbn']
        employeeID = request.form['employeeID'] 
        # If no employee ID is provided, change employee ID to NULL (None in Python)
        if employeeID == '': 
            employeeID = None
        # Set return date to NULL by default (None in Python)
        returnDate = None                                                             
        # Calculate check out date based upon current date
        todaysDate = date.today()                                                               
        todaysDate.strftime("%Y-%m-%d")
        checkOutDate = todaysDate
        # Calculate return date to be two weeks out from current date
        twoWeeks = timedelta(weeks = 2)
        dueDate = todaysDate + twoWeeks
              
        message = ""

        # Check for ID member
        searchMemberQuery = 'SELECT * FROM members WHERE member_ID = %s' % memberID
        searchMember = execute_query(db_connection, searchMemberQuery)
        
        # Check for ISBN
        searchISBNQuery = 'SELECT * FROM books WHERE ISBN = %s' % isbn
        searchISBN = execute_query(db_connection, searchISBNQuery)
        
        notValid = False
        # Check if the inputs are valid
        if searchMember.rowcount == 0:
            message = "No such member ID."
            notValid = True
        elif searchISBN.rowcount == 0:
            message = "No such ISBN."
            notValid = True
        elif employeeID is not None:
            searchEmployeeQuery = 'SELECT * FROM employees WHERE employee_ID = %s' % employeeID
            searchEmployee = execute_query(db_connection, searchEmployeeQuery)
            if searchEmployee.rowcount == 0:
                message = "No such employee ID."
                notValid = True

        # If inputs are not valid, show message
        if notValid is True:
            query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
            add_result = execute_query(db_connection, query).fetchall()
            return render_template("/transaction/checkOut.html", rows=add_result, query_message=message)

        query = 'SELECT number_of_copies, number_checked_out FROM books WHERE ISBN = %s' % isbn
        numOfBooks = execute_query(db_connection, query).fetchall()
        print(numOfBooks)
        result = str(numOfBooks[0])
        result = re.sub('[(),]', '', result)
        numOutAndAv = result.split(" ")
        print(numOutAndAv)
        numAv = int(numOutAndAv[0])
        numOut = int(numOutAndAv[1])
        print(type(numAv))
        print(type(numOut))
        
        # Insert new checked out book record
        # Check and update number of books checked out in Books table
        if numAv > numOut:
            updateBooks = 'UPDATE books SET number_checked_out = number_checked_out + 1 WHERE ISBN = %s' % isbn
            execute_query(db_connection, updateBooks)
            query = 'INSERT INTO checked_out_books (member_ID, employee_ID, ISBN, check_out_date, due_date, return_date) VALUES (%s, %s, %s, %s, %s, %s);' 
            data = ([memberID], employeeID, isbn, checkOutDate, dueDate, returnDate)
            execute_query(db_connection, query, data)
            message = "Book checked out."
        else:
            message = "No copies available."
            
        query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
        add_result = execute_query(db_connection, query).fetchall()
        
        return render_template("/transaction/checkOut.html", rows=add_result, query_message=message)

'''
Functionality: UPDATE - Updates return date.
'''
@app.route("/transaction/checkIn", methods=['GET', 'POST'])
def transactionCheckIn():
    print("Fetching and rendering check in book page.")
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
        result = execute_query(db_connection, query).fetchall()     
        print(result)
        
        return render_template("/transaction/checkIn.html", rows=result)

    # Updating check out date
    elif request.method == 'POST':
        memberID = request.form['memberID']
        isbn = request.form['isbn']
        # Set return date to today's date and format
        returnDate = date.today()                                                                                                                        
        returnDate.strftime("%Y-%m-%d")

        # Doing test query in order to see if transaction exists
        test_query = 'SELECT * FROM checked_out_books WHERE member_ID = %s AND ISBN = %s'
        test_data = ([memberID], isbn)
        test_result = execute_query(db_connection, test_query, test_data).fetchone()
        print(test_result)

        
        # If no such transaction exists, show message  
        if test_result == None:
            query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
            result = execute_query(db_connection, query).fetchall()
            message = "No such transaction found."

            return render_template("/transaction/checkIn.html", rows=result, query_message=message)  
        
        # Check if the book has been returned already
        dateQuery = 'SELECT return_date FROM checked_out_books WHERE member_ID = %s AND ISBN = %s'
        dateData = ([memberID], isbn)
        dateResult = execute_query(db_connection, dateQuery, dateData)
        # Make sure that transaction exist before trimming the string
        # print("Printing dateResult")
        # print(dateResult)
        rows = dateResult.rowcount
        dateStr = None
        if rows != 0:
            print(rows)
            dateResult = execute_query(db_connection, dateQuery, dateData).fetchall()
            # print(dateResult)
            dateStr = str(dateResult[rows - 1])
            dateStr = re.sub('[(),]', '', dateStr)
            print(dateStr)

            if dateStr != "None":
                # If the book has been return already, show message
                query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
                result = execute_query(db_connection, query).fetchall()
                message = "That book has been returned already."
                return render_template("/transaction/checkIn.html", rows=result, query_message=message)

        # Update transaction's return date
        query = 'UPDATE checked_out_books SET return_date = %s WHERE member_ID = %s AND ISBN = %s AND return_date IS NULL' 
        data = (returnDate, [memberID], isbn)
        execute_query(db_connection, query, data).fetchone() # CHECK one or all?

        # Decrease the number of books checked out by 1
        book_query = 'UPDATE books SET number_checked_out = number_checked_out - 1 WHERE ISBN = %s'
        book_data = ([isbn])   
        execute_query(db_connection, book_query, book_data)   

        # Display updated table
        query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
        update_result = execute_query(db_connection, query).fetchall()
        message = "Book checked in." 
        
        return render_template("/transaction/checkIn.html", rows=update_result, query_message=message)

'''
Functionality: UPDATE - Updates employee associated with transaction. (part 1)
Relationship: NULLable 1:M relationship between Checked_Out_Books and Employees
'''
@app.route("/transaction/selectToUpdate", methods=['GET', 'POST'])
def selectTransaction():
    
    print("Fetching and rendering select employee to update page.")
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
        result = execute_query(db_connection, query).fetchall()     
        print(result)
        
        return render_template("/transaction/selectToUpdate.html", rows=result)
    
    # Finding transaction to be updated
    elif request.method == 'POST':
        memberID = request.form['memberID']
        isbn = request.form['isbn']
        query = 'SELECT * FROM checked_out_books WHERE member_ID = %s AND ISBN = %s'
        data = ([memberID], isbn)
        transaction_result = execute_query(db_connection, query, data).fetchone()
        print(transaction_result)

        # If no such transaction exists, show message  
        if transaction_result == None:
            query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
            result = execute_query(db_connection, query).fetchall()
            message = "No such transaction found."

            return render_template("/transaction/selectToUpdate.html", rows=result, query_message=message)

        # Otherwise, render pre-populated update form
        return render_template("/transaction/updateForm.html", transaction=transaction_result)

'''
Functionality: UPDATE - Updates employee associated with transaction. (part 2)
Relationship: NULLable 1:M relationship between Checked_Out_Books and Employees
'''
@app.route("/transaction/updateForm", methods=['POST'])
def updateTransactions():

    print("Fetching and rendering update results page.")
    db_connection = connect_to_database()

    # Get updated employee value from pre-populated form
    if request.method == 'POST':
        checkedOutBookID = request.form['checkedOutBookID']
        memberID = request.form['memberID']
        employeeID = request.form['employeeID']
        isbn = request.form['isbn']
        checkOutDate = request.form['checkOutDate']
        dueDate = request.form['dueDate']
        returnDate = request.form['returnDate']
        # If no employee_ID is provided, change employee_ID to NULL (None in Python)
        if employeeID == '': 
            employeeID = None

        # Do test query to see if employee exists
        if employeeID is not None:
                test_query = 'SELECT * FROM employees where employee_ID = %s'
                test_data = ([employeeID])
                test_result = execute_query(db_connection, test_query, test_data).fetchone()

                if test_result == None:
                    query = 'SELECT * FROM checked_out_books WHERE member_ID = %s AND ISBN = %s'
                    data = ([memberID], isbn)
                    transaction_result = execute_query(db_connection, query, data).fetchone()
                    print(transaction_result)
                    message = "No such employee exists."
                    
                    return render_template("/transaction/updateForm.html", transaction=transaction_result, query_message=message)

        # Update associated employee
        query = 'UPDATE checked_out_books SET member_ID = %s, employee_ID = %s, ISBN = %s, check_out_date = %s, due_date = %s, return_date = %s  WHERE checked_out_book_ID = %s' 
        data = ([memberID], [employeeID], [isbn], checkOutDate, dueDate, returnDate, [checkedOutBookID])
        update_result = execute_query(db_connection, query, data)

        # Display updated row
        query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN WHERE checked_out_books.checked_out_book_ID = %s'
        data = ([checkedOutBookID])
        updated_transaction = execute_query(db_connection, query, data)  

        # Display all rows
        query = 'SELECT checked_out_books.member_ID, members.first_name, members.last_name, checked_out_books.ISBN, books.title, checked_out_books.check_out_date, checked_out_books.due_date, checked_out_books.return_date, checked_out_books.employee_ID FROM checked_out_books INNER JOIN members ON checked_out_books.member_ID = members.member_ID INNER JOIN books ON checked_out_books.ISBN = books.ISBN'
        result = execute_query(db_connection, query).fetchall() 
        
        return render_template("/transaction/updateResult.html", updatedRows=updated_transaction, allRows=result)
#--------------------------------------------------------

'''
Entity: Books
'''
#--------------------------------------------------------
# Books Routing

'''
Functionality: SELECT
'''
@app.route("/book/lookUp", methods=['GET', 'POST'])
def bookLookUp():
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT books.ISBN, books.title, books.publication_year, books.number_of_copies, books.number_checked_out, authors.first_name, authors.last_name FROM books INNER JOIN book_author ON book_author.ISBN = books.ISBN INNER JOIN authors ON authors.author_ID = book_author.author_ID;'
        result = execute_query(db_connection, query)
        return render_template("/book/lookUp.html", rows=result, title=result)
    
    # Find book by title
    elif request.method == 'POST':
        title = request.form['titleSelect']
        print(title)
        
        # Get the data to put on dropdown menu
        query = 'SELECT books.ISBN, books.title, books.publication_year, books.number_of_copies, books.number_checked_out, authors.first_name, authors.last_name FROM books INNER JOIN book_author ON book_author.ISBN = books.ISBN INNER JOIN authors ON authors.author_ID = book_author.author_ID;'
        result = execute_query(db_connection, query)
        
        # Get the result to display
        selectQuery = 'SELECT books.ISBN, books.title, books.publication_year, books.number_of_copies, books.number_checked_out, authors.first_name, authors.last_name FROM books INNER JOIN book_author ON book_author.ISBN = books.ISBN INNER JOIN authors ON authors.author_ID = book_author.author_ID WHERE title = %s'
        data = ([title])
        selectResult = execute_query(db_connection, selectQuery, data)

        # If no such book exists, show message  
        if result == ():
            query = 'SELECT books.ISBN, books.title, books.publication_year, books.number_of_copies, books.number_checked_out, authors.first_name, authors.last_name FROM books INNER JOIN book_author ON book_author.ISBN = books.ISBN INNER JOIN authors ON authors.author_ID = book_author.author_ID;'
            result = execute_query(db_connection, query).fetchall()
            message = "No such book found."

            return render_template("/book/lookUp.html", rows=result, query_message=message)
        
        # Otherwise, display book
        return render_template("/book/lookUp.html", rows=selectResult, title=result)

'''
Functionality: INSERT
Relationship: M:M between Books and Authors
'''
@app.route("/book/add", methods=['GET', 'POST'])
def bookAdd():
    '''
    When add book, check if author exits. If author doesn't exist,
    execute a query to add the author to author table. Else, add the book to the book table.
    
    Then go and add the relationship in book_author table.
    '''
    db_connection = connect_to_database()
    
    # Initial visit to apge
    if request.method == 'GET':
        query = 'SELECT books.ISBN, books.title, books.publication_year, books.number_of_copies, books.number_checked_out, authors.first_name, authors.last_name FROM books INNER JOIN book_author ON book_author.ISBN = books.ISBN INNER JOIN authors ON authors.author_ID = book_author.author_ID;'
        result = execute_query(db_connection, query)
        return render_template("/book/add.html", rows=result)
    
    # Add book
    elif request.method == 'POST':
        ISBN = request.form['ISBN']
        title = request.form['title']
        year = request.form['publicationYear']
        author = request.form['author']

        # Split the name string into first and last name
        first_name, last_name = author.split(' ', 1)


        # Perform a SELECT to check if author already exists in the authors table
        searchAuthorQuery = 'SELECT * FROM authors WHERE first_name = %s AND last_name = %s'
        data = (first_name, last_name)
        searchResult = execute_query(db_connection, searchAuthorQuery, data)
        authorExists = "Author already exists, proceding to add book."
        bookExists = "Book already exists, incremented count."
        relationshipExists = "Book_author relationship already exists."
        if searchResult.rowcount == 0: # Triggered when the author doesn't exist in the authors table
            insertAuthor = 'INSERT INTO authors (first_name, last_name) VALUES (%s, %s)'
            execute_query(db_connection, insertAuthor, data)
            authorExists = "Added author %s" % author
        
        # Check if book is already on the table.
        searchBookQuery = 'SELECT * FROM books WHERE ISBN = %s' % ISBN
        # data = ISBN
        searchResult = execute_query(db_connection, searchBookQuery)
        if searchResult.rowcount == 0:  # Book is no in the books table, add book.
            insertBookQuery = 'INSERT INTO books (ISBN, title, publication_year) VALUES (%s, %s, %s)'
            data = (ISBN, title, year)
            execute_query(db_connection, insertBookQuery, data)
            bookExists = "Book wasn't in the table, added book to the table."

            # Create the book_author relationship
            authorIDQuery = 'SELECT author_ID FROM authors WHERE first_name = %s AND last_name = %s'
            data = (first_name, last_name)
            authorIDResult = execute_query(db_connection, authorIDQuery, data)
            authorID = authorIDResult.fetchall()
            authorIDstring = str(authorID[0])
            authorIDstring = re.sub('[(),]', '', authorIDstring)

            insertQuery = 'INSERT INTO book_author (author_ID, ISBN) VALUES (%s, %s)'
            data = (authorIDstring, ISBN)
            execute_query(db_connection, insertQuery, data)
            relationshipExists = "Added relationship to book_author table."
        # Book is already in the books table, increment count.
        else:
            updateBookQuery = 'UPDATE books SET number_of_copies = number_of_copies + 1 WHERE ISBN = %s' % ISBN
            # data = (ISBN)
            execute_query(db_connection, updateBookQuery)

        # Display updated table
        query = 'SELECT books.ISBN, books.title, books.publication_year, books.number_of_copies, books.number_checked_out, authors.first_name, authors.last_name FROM books INNER JOIN book_author ON book_author.ISBN = books.ISBN INNER JOIN authors ON authors.author_ID = book_author.author_ID;'
        result = execute_query(db_connection, query)
        
        return render_template("/book/add.html", authorExists=authorExists, bookExists=bookExists, relationship=relationshipExists, rows=result)

'''
Functionality: DELETE
'''
@app.route("/book/remove", methods = ['GET', 'POST'])
def bookRemove():
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT books.ISBN, books.title, books.publication_year, books.number_of_copies, books.number_checked_out, authors.first_name, authors.last_name FROM books INNER JOIN book_author ON book_author.ISBN = books.ISBN INNER JOIN authors ON authors.author_ID = book_author.author_ID;'
        result = execute_query(db_connection, query)
        return render_template("/book/remove.html", rows=result)
    
    # Remove book
    elif request.method == 'POST':
        ISBN = request.form['ISBN']

        # Doing test query in order to see if book exists
        test_query = 'SELECT * FROM books WHERE ISBN = %s'
        test_data = ([ISBN])
        test_result = execute_query(db_connection, test_query, test_data).fetchone()
        print(test_result)

        # If no such books exists, show message  
        if test_result == None:
            query = 'SELECT books.ISBN, books.title, books.publication_year, books.number_of_copies, books.number_checked_out, authors.first_name, authors.last_name FROM books INNER JOIN book_author ON book_author.ISBN = books.ISBN INNER JOIN authors ON authors.author_ID = book_author.author_ID;'
            result = execute_query(db_connection, query).fetchall()
            message = "No such book found."

            return render_template("/book/remove.html", rows=result, query_message=message)
        
        # Get the number of copies of the book
        query = 'SELECT number_of_copies FROM books WHERE ISBN = %s' % ISBN
        searchResult = execute_query(db_connection, query).fetchall()
        numOfBooks = str(searchResult[0])
        numOfBooks = re.sub('[(),]', '', numOfBooks)
        print(searchResult)
        print(numOfBooks)

        
        if int(numOfBooks) > 1:
            # If there are more than 1 book, decrement the number of copies by 1
            print("More than 1")
            updateBookQuery = 'UPDATE books SET number_of_copies = number_of_copies - 1 WHERE ISBN = %s' % ISBN
            execute_query(db_connection, updateBookQuery)
        else:
            # If there's only 1 book remaining, delete the book from the table
            deleteBookQuery = 'DELETE FROM books WHERE ISBN = %s' % ISBN
            execute_query(db_connection, deleteBookQuery)

        # Display resulting table
        query = 'SELECT books.ISBN, books.title, books.publication_year, books.number_of_copies, books.number_checked_out, authors.first_name, authors.last_name FROM books INNER JOIN book_author ON book_author.ISBN = books.ISBN INNER JOIN authors ON authors.author_ID = book_author.author_ID;'
        result = execute_query(db_connection, query)
        message = "Book removed."

        return render_template("/book/remove.html", rows=result, query_message=message)
#--------------------------------------------------------

'''
Entity: Authors
'''
#--------------------------------------------------------
# Authors Routing

'''
Functionality: INSERT
'''
@app.route("/author/lookUp", methods=['GET', 'POST'])
def authorLookUp():
    
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT * FROM authors'
        result = execute_query(db_connection, query)
        return render_template("/author/lookUp.html", rows=result)
    
    # Look up author
    elif request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        query = 'SELECT * FROM authors WHERE first_name = %s AND last_name = %s'
        data = (fname, lname)
        result = execute_query(db_connection, query, data).fetchall()
        
        # If no such author exists, show message  
        if result == ():
            query = 'SELECT * FROM authors'
            result = execute_query(db_connection, query).fetchall()
            message = "No such author found."

            return render_template("/author/lookUp.html", rows=result, query_message=message) 
        
        # Otherwise, display result
        return render_template("/author/lookUp.html", rows=result)

'''
Functionality: INSERT
'''
@app.route("/author/add", methods=['GET', 'POST'])
def authorAdd():
    
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT * FROM authors'
        result = execute_query(db_connection, query)
        return render_template("/author/add.html", rows=result)
    
    # Add author
    elif request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']

        # First check to make sure that author does not already exist
        test_query = "SELECT first_name, last_name FROM authors WHERE first_name = %s AND last_name = %s"
        test_data = (fname, lname)
        test_result = execute_query(db_connection, test_query, test_data).fetchall()
        print(test_result)

        # If author already exists
        if test_result != ():
            no_add_query = 'SELECT * FROM authors'
            no_add_result = execute_query(db_connection, no_add_query)
            message = "Author is already in database."
            return render_template("/author/add.html", rows=no_add_result, query_message=message)

        # Otherwise, insert author
        query = 'INSERT INTO authors (first_name, last_name) VALUES (%s, %s)'
        data = (fname, lname)
        result = execute_query(db_connection, query, data)

        # Display resulting table
        add_query = 'SELECT * FROM authors'
        add_result = execute_query(db_connection, add_query)
        message = "Author added."
        
        return render_template("/author/add.html", rows=add_result, query_message=message)

#--------------------------------------------------------

'''
Entity: Employees
'''
#--------------------------------------------------------
# Employees Routing

'''
Functionality: SELECT
'''
@app.route("/employee/lookUp", methods=['GET', 'POST'])
def employeeLookUp():
    
    print("Fetching and rendering look up employee page.")
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT employee_ID, first_name, last_name from employees'
        result = execute_query(db_connection, query).fetchall()     
        print(result)
        
        return render_template("/employee/lookUp.html", rows=result)
    
    # Finding employee
    elif request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        query = 'SELECT employee_ID, first_name, last_name from employees where first_name = %s AND last_name = %s'
        data = (fname, lname)
        search_result = execute_query(db_connection, query, data).fetchall()

        # If no such employee exists, show message  
        if search_result == ():
            query = 'SELECT employee_ID, first_name, last_name from employees'
            result = execute_query(db_connection, query).fetchall()
            message = "No such employee found."

            return render_template("/employee/lookUp.html", rows=result, query_message=message) 

        # Otherwise, display result
        return render_template("/employee/lookUp.html", rows=search_result)

'''
Functionality: INSERT
'''
@app.route("/employee/add", methods=['GET', 'POST'])
def employeeAdd():
    
    print("Fetching and rendering add employee page.")
    db_connection = connect_to_database()
    
    # Initial visit to page
    if request.method == 'GET':
        query = 'SELECT employee_ID, first_name, last_name from employees'
        result = execute_query(db_connection, query).fetchall()     
        print(result)

        return render_template("/employee/add.html", rows=result)

    # Adding employee
    elif request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        query = 'INSERT INTO employees (first_name, last_name) VALUES (%s, %s)'
        data = (fname, lname)
        execute_query(db_connection, query, data).fetchall()       

        # Display result
        query = 'SELECT employee_ID, first_name, last_name from employees'
        add_result = execute_query(db_connection, query).fetchall()
        message = "Employee added."
        
        return render_template("/employee/add.html", rows=add_result, query_message=message)

#--------------------------------------------------------


#--------------------------------------------------------
# Database testing
@app.route("/dbTest")
def dbTest():
    db_connection = connect_to_database()
    query = "SELECT * from authors"
    result = execute_query(db_connection, query)
    return render_template('db_test.html', rows=result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 
