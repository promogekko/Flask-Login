from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
from flask_script import Manager
from werkzeug import generate_password_hash, check_password_hash
from contextlib import closing
import os

mysql = MySQL()
app = Flask(__name__)
manager = Manager(app)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/initDB')
def initDB():
    app.config['MYSQL_DATABASE_USER'] = os.environ['DB_USER_USERNAME']
    app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['DB_USER_PASSWORD']
    app.config['MYSQL_DATABASE_DB'] = 'BucketList'
    app.config['MYSQL_DATABASE_HOST'] = 'mysql'
    mysql.init_app(app)
    try:
        mysql.connect()
        return json.dumps({'message':'initDB !'})
    except Exception as e:
        return json.dumps({'error':str(e)})

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name     = request.form['inputName']
        _email    = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            
            with closing (mysql.connect()) as conn:
                with closing(conn.cursor()) as cursor:
                    _hashed_password = generate_password_hash(_password)
                    cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
                    data = cursor.fetchall()

                    if len(data) is 0:
                        conn.commit()
                        return json.dumps({'message':'User created successfully !'})
                    else:
                         return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})


if __name__ == "__main__":
    manager.run()
