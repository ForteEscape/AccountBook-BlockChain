from flask import Flask, render_template, jsonify, request, redirect, session
import json
from textwrap import dedent
from uuid import uuid4
from blockchain import BlockChain
from datetime import datetime
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'plz'
app.config['MYSQL_DATABASE_DB'] = 'accountBook'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

app.secret_key = '???'

# 홈화면
@app.route('/')
def home_intro():
    return render_template('intro.html', name="home_intro")

# 회비납부 화면
@app.route('/current')
def current():
    return render_template('current.html', name="current")

# 장부화면
@app.route('/home')
def home_main():
    return render_template('home.html', name="home_main")


# 장부추가 아직 수정해야함
@app.route('/addAccount', methods=['POST'])
def addAcount():
    try:
        _use_name = request.form['use_name']
        _use_description = request.form['use_d']
        _use_money = int(request.form['use_money'])
        _use_date = int(request.form['use_date'])
        _write_name = 'writer'
        _write_date = 20180101
        print(type(_write_date))

        conn = mysql.connect()
        cursor = conn.cursor()
        print((_use_name, _use_description, _use_money, _use_date, _write_date, _write_name))
        print((type(_use_name), type(_use_description), type(_use_money), type(_use_date), type(_write_date), type(_write_name)))
        cursor.callproc('sp_addAccount', (_use_name, _use_description, _use_money, _use_date, _write_date, _write_name))
        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            return redirect('/home')
        else:
            return render_template('error.html', error='An error occurred!')

    except Exception as e:
        print(str(e))
        return render_template('error.html', error=str(e))

# 로그인
@app.route('/intro', methods=['POST','GET'])
def validateLogin():
    if request.method == 'POST':
        try:
            _email = request.form['inputEmail']
            _password = request.form['inputPassword']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_validateLogin',(_email,))
            data = cursor.fetchall()

            if len(data) > 0:
                if(check_password_hash(str(data[0][1]), _password)): # user password compared
                    session['user'] = data[0][0] # user name
                    return redirect('/')
                else:
                    return render_template('intro.html', loginError='잘못된 Email이거나 잘못된 Password 입니다')
            else:
                return render_template('intro.html', loginError='잘못된 Email이거나 잘못된 Password 입니다')

        except Exception as e:
            return render_template('error.html', error=str(e))

    else:
        return render_template('intro.html', name="intro")


# 회원가입
@app.route('/joinIn', methods=['POST', 'GET'])
def joinIn():
    if request.method == 'POST':
        try:
            _email = request.form['inputEmail']
            _password = request.form['inputPassword'] # 특수문자 허용 x
            _name = request.form['inputName']
            _gender = int(request.form['inputGender']) # man=0, woman=1
            _grade = int(0) # default, 관리자=1

            if _email and _password and _name:
                conn = mysql.connect()
                cursor = conn.cursor()
                _hashed_password = generate_password_hash(_password)
                cursor.callproc('sp_createUser', (_email, _hashed_password, _name, _gender, _grade))
                data = cursor.fetchall()

                if len(data) is 0:
                    conn.commit()
                    return render_template('joinSuccess.html',join=_name + " 님의 아이디(이메일)은 '" +  _email + "' 입니다.")
                else:
                    return render_template('error.html',error=str(data[0]))
            else:
                return render_template('join.html',error="모든 항목을 다 채워주세요.")

        except Exception as e:
            return render_template('error.html', error=str(e))

    else:
        return render_template('join.html', name="join")


# 통계 화면
@app.route('/stat')
def stat():
    return render_template('stat.html', name="stat")


if __name__ == '__main__':
    app.run()
