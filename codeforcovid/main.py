from flask import Flask, request, render_template, redirect, url_for, flash, session
import sqlite3
'''import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="yourpassword",
	database="fooddb"
)

mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE tbl_images (id INTEGER PRIMARY KEY AUTOINCREMENT, name BLOB)")'''

app = Flask(__name__, static_url_path='/static/')
app.secret_key = 'sayglenn'

try:
  con = sqlite3.connect("konnect.db")
  con.execute("CREATE TABLE User" + "(ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT UNIQUE, Password TEXT, AmountDonated TEXT, ItemsDonated TEXT, Bio TEXT)")
  con.commit()
  con.close()
except:
  pass

try:
  words = sqlite3.connect('konnect.db')
  words.execute("CREATE TABLE Library" + "(lib_id INTEGER PRIMARY KEY AUTOINCREMENT, Number INTEGER , Service TEXT)")
  words.commit()
  words.close()
except: # my if else work alr but i need try to input data and search
  pass

try:
  words = sqlite3.connect('konnect.db')
  words.execute("CREATE TABLE Donor" + "(donor_id INTEGER PRIMARY KEY AUTOINCREMENT, donator TEXT, amount INTEGER)")
  words.commit()
  words.close()
except:
  pass

@app.route('/') # Index homepage
def index():
  return render_template('index.html')

@app.route('/login/', methods=['GET', 'POST']) # Login page
def login(): # if already registered (meaning password is saved into databank)
  if request.method == 'POST':   
    username = str(request.form['username_input'])
    password = str(request.form['password_input'])
    konnect = sqlite3.connect("konnect.db")
    # Excecute query to find username and password
    cursor = konnect.execute("SELECT Name FROM User WHERE Name = ? AND Password = ?",(username, password))
    for row in cursor:
      if username == row[0]: # Username and password match
        session.permanent = True # Sign user into session
        session['user'] = username
        konnect.commit()
        konnect.close()
        return render_template('home.html', username=username)
      else: # Username and password do not match
        flash('Wrong Password or Username')
        print('sup')
        return redirect(url_for('login'))
    flash('Wrong Password or Username')
  return render_template('login.html') # Request.method == 'GET'

@app.route('/signup/', methods=['GET', 'POST']) # if user has no account
def signup():
  if request.method == 'POST':
    username = str(request.form['username_input'])
    password = str(request.form['password_input'])
    konnect = sqlite3.connect("konnect.db")
    cursor = konnect.execute("SELECT Name FROM User WHERE Name = ?", (username,)) # will be empty if username is not found
    for row in cursor:
      if username == row[0]: # username found therefore cannot create
        error = 'Username already taken'
        return render_template('signup.html', error=error)
    
    amt = 0.00 # Profile initialisation
    itm = 0
    bio = 'Biography incomplete'
    konnect.execute("INSERT INTO User(Name, Password, AmountDonated, ItemsDonated, Bio) " + "VALUES(?,?,?,?,?)",(username,password, amt, itm, bio))
    konnect.commit()
    konnect.close()
    return render_template('home.html', username=username)
  return render_template('signup.html')

@app.route('/home/')
def home():
  if 'user' in session:
    user = session['user']
    return render_template('home.html', username = user)
  return render_template('home.html')
  
@app.route('/food/')
def food():
  return render_template('food.html')

@app.route('/money/', methods=['GET','POST'])
def money():
  user = session['user']
  if request.method == 'POST':
    donator = str(request.form['donator'])
    donation = float(request.form['donation'])
    donation = float("{:.2f}".format(donation))
    con = sqlite3.connect('konnect.db')
    con.execute('''INSERT INTO Donor(donator, amount)''' + '''VALUES(?,?)''',(donator,donation))
    thanks = 'Thank you for your kind donation'
    cursor =  con.execute('''SELECT AmountDonated from User WHERE Name = ?''', (user,))
    for row in cursor:
      amt = row[0]

    total_donation_amt = float(amt) + float(donation)
    total_donation_amt = float("{:.2f}".format(total_donation_amt))

    con.execute('''UPDATE User SET AmountDonated = ? where Name = ?''', (total_donation_amt, user))
    con.commit()
    con.close()
    return redirect(url_for('money', thanks=thanks))
    
  con = sqlite3.connect('konnect.db')
  cursor = con.execute('''SELECT donator, amount FROM Donor ORDER BY amount DESC LIMIT 10''')
  position = []
  name = []
  amount = []
  count = 1
  for row in cursor:
    position.append(count)
    name.append(row[0])
    amount.append(row[1])
    count += 1
  
  con.commit()
  con.close()
  position2 = position
  table_rows = zip(position, position2, name, amount)
  return render_template('money.html', donors=table_rows)

@app.route('/donate/')
def donate():
  return render_template('home.html')

@app.route('/receive/')
def receive():
  return render_template('options.html')



@app.route('/others/', methods=['GET', 'POST'])
def others():
  if request.method=='GET':
    return render_template('others.html')
  #if request.method=='post':
  if 'services' in request.form:
    library = sqlite3.connect('konnect.db')
    service = request.form['services']
    number = request.form['number']
    library.execute("INSERT INTO Library(Number, Service) " + "VALUES(?,?)",(number,service))
    library.commit()
    library.close()
    return render_template('others.html')
      
  '''
  def within_match(array):
    matching = []
    term = input("Enter term: ")
    for word in array:
      if term in word: # if term exist within in word
        matching.append(word)
        print(word)
  '''      
  if 'searching' in request.form:
    matching = []
    term = request.form['searching']
    library = sqlite3.connect('konnect.db')
    cursor = library.execute("SELECT Service FROM Library")
    for word in cursor:
      words = word[0]
      if term in words: # if term exist within in word
        matching.append(words)
    for i in matching:
      return render_template('available.html', matching=matching)
  
  return render_template('others.html')

@app.route('/profile/')
def profile():
  if 'user' in session:
    user = session['user']
    con = sqlite3.connect('konnect.db')
    cursor = con.execute('''SELECT AmountDonated, ItemsDonated, Bio FROM User''')
    for item in cursor:
      temp = float(item[0])
      amtdon = "{:.2f}".format(temp)
      itmdon, bio = item[1], item[2]
    return render_template('profile.html', user=user, amtdon=amtdon, itmdon=itmdon, bio=bio)

@app.route('/logout/')
def logout():
  if 'user' in session:
    user = session['user']
    session.pop('user', None)
    flash('You have been logged out {}'.format(user))
  return redirect(url_for('login'))
  
if __name__ == '__main__':
  app.run(host = '0.0.0.0', port = 8000)