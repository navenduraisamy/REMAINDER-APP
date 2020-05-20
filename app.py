from flask import Flask,render_template,url_for,request,redirect,flash,session
from flask_mysqldb import MySQL
import yaml
from datetime import date
from werkzeug.security import generate_password_hash,check_password_hash


app=Flask(__name__)
app.secret_key = "rasathavalasu"


#configure db
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']

mysql=MySQL(app)

@app.route('/',methods=['POST','GET'])
def home():
    if request.method=="POST":
        logincred=request.form
        email=logincred['email']
        pwd=logincred['password']
        cur=mysql.connection.cursor()
        result=cur.execute("SELECT * from users where email=%s",(email,))
        if result == 0:
            flash("Invalid email. Try again.")
            return redirect(url_for('home'))
        else:
            data=cur.fetchall()
            hashedpwd=data[0][4]
            validate = check_password_hash(hashedpwd,pwd)
            if validate == True:
                session['user']=data[0][0]
                flash("Login successful.")
                return redirect(url_for('users'))
            else:
                flash("Invalid password. Try again.")
                return redirect(url_for('users'))
    else:
        return render_template("index.html")

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        signup=request.form
        fname=signup['firstname']
        lname=signup['lastname']
        email=signup['email']
        pwd1=signup['password']
        pwd2=signup['password2']
        cur1 = mysql.connection.cursor()
        result = cur1.execute('SELECT * from users where email=%s',(email,))
        if result == 0:
            if(pwd1 == pwd2):
                hashedpwd = generate_password_hash(pwd1)
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO users(firstname,lastname,email,password) VALUES(%s,%s,%s,%s)",(fname,lname,email,hashedpwd))
                mysql.connection.commit()
                cur.close()
                flash("Account created successfully! Login to proceed")
                return redirect(url_for('home'))
            else:
                flash("Passwords don't match")
                return redirect(url_for('signup'))
        else:
            flash("Email already taken!")
            return redirect(url_for('signup'))
    else:
        return render_template("signup.html")

@app.route('/users',methods=['POST','GET'])
def users():
    if "user" in session:
        if request.method=='POST':
            event = request.form
            event_id = event['event_id']
            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM events WHERE event_id=%s',(event_id,))
            cur.connection.commit()
            cur.close()
            return redirect(url_for('users'))
            #return render_template('hello.html',id=event_id)
        else:
            user_id=session['user']
            cur1=mysql.connection.cursor()
            cur2=mysql.connection.cursor()
            today=date.today()
            result1=cur1.execute("SELECT * FROM events WHERE user_id=%s AND date>=%s ORDER BY date DESC ",(user_id,today))
            result2=cur2.execute("SELECT * FROM events WHERE user_id=%s AND date<%s ORDER BY date DESC ",(user_id,today))
            if result1 > 0 and result2 > 0:
                events1=cur1.fetchall()
                events2=cur2.fetchall()
                return render_template('users.html',events1=events1,events2=events2)
            elif result1 > 0 and result2==0:
                events1=cur1.fetchall()
                return render_template('users.html',events1=events1,events2=None)
            elif result2 > 0 and result1==0:
                events2=cur2.fetchall()
                return render_template('users.html',events1=None,events2=events2)
            else:
                return render_template('users.html',events1=None,events2=None)
    else:
        return redirect(url_for('home'))

@app.route('/addevent',methods=['POST','GET'])
def addevent():
    if "user" in session:
        if request.method=='POST':
            event=request.form
            name=event['eventname']
            desc=event['eventdesc']
            date=event['eventdate']
            user_id=session['user']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO events(user_id,title,description,date) VALUES(%s,%s,%s,%s)",(user_id,name,desc,date))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('users'))
        else:
            return render_template('create_event.html')
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    if "user" in session:
        session.pop("user",None)
        flash('You have been logged out.')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
if __name__ =='__main__':
    app.run(debug=True,threaded = True )
