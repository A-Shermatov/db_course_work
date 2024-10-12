import datetime
import hashlib

from flask import Flask, jsonify, request

# MySQL imports
from flask_mysqldb import MySQL
from environments import DB

from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

app.config['MYSQL_USER'] = DB['DB_USER']
app.config['MYSQL_PASSWORD'] = DB['DB_PASSWORD']
app.config['MYSQL_DB'] = DB['DB_NAME']
mysql = MySQL(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# USERS=================================================================================


@app.route('/users/', methods=['POST'])
def create_user() -> jsonify:
    data = {key: val for key, val in request.get_json().items() if val != ''}
    if not check(data) or \
            'username' not in data or \
            'password' not in data or \
            'role' not in data:
        return jsonify({'status': 'Bad Request'}), 400
    if 'name' in data:
        if 'surname' in data:
            answer = create_user_func(_name=data['name'], _surname=data['surname'], _username=data['username'],
                                      _email=data['email'], _password=data['password'], _role=data['role'])
        else:
            answer = create_user_func(_surname=data['surname'], _username=data['username'],
                                      _email=data['email'], _password=data['password'], _role=data['role'])
    else:
        answer = create_user_func(_username=data['username'], _email=data['email'],
                                  _password=data['password'], _role=data['role'])
    print(answer)
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400
    return jsonify({'status': 'Created', 'user_id': answer[1]}), 201


@app.route("/users/login/", methods=['POST'])
def login_user() -> jsonify:
    data = {key: val for key, val in request.get_json().items() if val != ''}
    if 'username' not in data or \
            'password' not in data or \
            'role' not in data or \
            'username' in data and len(data['username']) > 15 \
            or 'role' in data and len(data['role']) > 10:
        return jsonify({'status': 'Bad Request'}), 400
    answer = login_user_func(_username=data['username'], _password=data['password'], _role=data['role'])
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400
    return jsonify({'status': 'OK', 'user_id': answer[1]}), 200


@app.route("/users/", methods=['PUT'])
def update_user() -> jsonify:
    data = {key: val for key, val in request.get_json().items() if val != ''}
    if not check(data):
        return jsonify({'status': 'Bad Request'}), 400
    answer = update_user_func(data=data)
    if answer[0] == "Failed":
        return jsonify({'status': 'Bad Request'}), 400
    return jsonify({'status': 'Accepted', 'user_id': data['user_id']}), 202


@app.route("/users/", methods=['GET'])
def search_user() -> jsonify:
    user_id = request.args.get('user_id')
    data = {
        'user_id': user_id,
        'name': request.args.get('name'),
        'surname': request.args.get('surname'),
        'username': request.args.get('username'),
        'email': request.args.get('email'),
        'role': request.args.get('role'),
    }
    data = {key: val for key, val in data.items() if val}
    if 'user_id' not in data:
        return jsonify({'status': 'Failed'}), 400
    answer = search_user_func(data)
    return jsonify({'status': 'OK', 'user_id': user_id, 'users': answer[1]}), 200


@app.route("/users/", methods=['DELETE'])
def delete_user() -> jsonify:
    data = {key: val for key, val in request.get_json().items() if val != ''}
    if 'user_id' not in data or 'delete_user_id' not in data:
        return jsonify({'status': 'Bad Request'}), 400
    answer = delete_user_func(data)
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400
    return jsonify({'status': 'OK'}), 200


# SUBJECTS=================================================================================


@app.route("/subjects/", methods=['POST'])
def create_subject() -> jsonify:
    data = {key: val for key, val in request.get_json().items() if val != ''}
    if 'user_id' not in data or 'title' not in data or 'title' in data and len(data['title']) > 20:
        return jsonify({'status': 'Bad Request'}), 400
    answer = create_subject_func(data)
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400
    return jsonify({'status': 'Created', 'user_id': data['user_id'], 'subject_id': answer[1]}), 201


@app.route("/subjects/", methods=['PUT'])
def update_subject() -> jsonify:
    data = {key: val for key, val in request.get_json().items() if val != ''}
    if 'user_id' not in data or 'subject_id' not in data or \
            'title' not in data or 'title' in data and len(data['title']) > 20:
        return jsonify({'status': 'Bad Request'}), 400
    answer = update_subject_func(data)
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400
    return jsonify({'status': 'OK', 'user_id': data['user_id'], 'subject_id': data['subject_id']}), 200


@app.route("/subjects/", methods=['GET'])
def search_subject() -> jsonify:
    data = {
        'user_id': request.args.get('user_id'),
        'title': request.args.get('title')
    }
    data = {key: val for key, val in data.items() if val}
    if 'user_id' not in data:
        return jsonify({'status': 'Bad Request'}), 400

    answer = search_subject_func(data)
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400

    return jsonify({'status': 'OK', 'user_id': data['user_id'], 'subjects': answer[1]}), 200


@app.route("/subjects/", methods=['DELETE'])
def delete_subject() -> jsonify:
    data = {key: val for key, val in request.get_json().items() if val != ''}
    if 'user_id' not in data or 'delete_subject_id' not in data:
        return jsonify({'status': 'Bad Request'}), 400
    answer = delete_subject_func(data)
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400
    return jsonify({'status': 'OK'}), 200


# THEMES=================================================================================


@app.route("/themes/", methods=['POST'])
def create_theme() -> jsonify:
    data = {key: val for key, val in request.get_json().items() if val != ''}
    if 'user_id' not in data or 'subject_id' not in data or 'title' not in data or \
            'title' in data and len(data['title']) > 20:
        return jsonify({'status': 'Bad Request'}), 400
    answer = create_theme_func(data)
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400
    return jsonify({'status': 'Created', 'user_id': data['user_id'],
                    'subject_id': data['subject_id'], 'theme_id': answer[1]}), 201


@app.route("/themes/", methods=['PUT'])
def update_theme() -> jsonify:
    data = {key: val for key, val in request.get_json().items() if val != ''}
    if 'user_id' not in data or 'subject_id' not in data or \
            'theme_id' not in data or 'title' in data and len(data['title']) > 20:
        return jsonify({'status': 'Bad Request'}), 400
    answer = update_theme_func(data)
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400
    return jsonify({'status': 'OK', 'user_id': data['user_id'],
                    'subject_id': data['subject_id'], 'theme_id': data['theme_id']}), 200


@app.route("/themes/", methods=['GET'])
def search_theme() -> jsonify:
    data = {
        'user_id': request.args.get('user_id'),
        'title': request.args.get('title')
    }
    data = {key: val for key, val in data.items() if val}
    if 'user_id' not in data:
        return jsonify({'status': 'Bad Request'}), 400

    answer = search_theme_func(data)
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400

    return jsonify({'status': 'OK', 'user_id': data['user_id'], 'themes': answer[1]}), 200


@app.route("/themes/", methods=['DELETE'])
def delete_theme() -> jsonify:
    data = {key: val for key, val in request.get_json().items() if val != ''}
    if 'user_id' not in data or 'subject_id' not in data or 'delete_theme_id' not in data:
        return jsonify({'status': 'Bad Request'}), 400
    answer = delete_theme_func(data)
    if answer[0] == 'Failed':
        return jsonify({'status': 'Bad Request'}), 400
    return jsonify({'status': 'OK'}), 200


# Functions=======================================================================================


def email_validate(email: str) -> bool:
    try:
        validate_email(email)
    except EmailNotValidError:
        return False
    return True


def check(data: dict) -> bool:
    if 'email' in data and (len(data['email']) > 15 or not email_validate(data['email'])) or \
            'name' in data and len(data['name']) > 20 or \
            'surname' in data and len(data['surname']) > 20 or \
            'username' in data and len(data['username']) > 15 or \
            'role' in data and len(data['role']) > 10:
        return False
    return True


def search(data, query):
    if not(len(data.keys()) == 1 and data.get('user_id', None) is not None):
        if len(data.keys()) > 0:
            query += ' WHERE'
        values = []
        for k, v in data.items():
            if k != 'user_id':
                query += ' ' + k + '="' + v + '" AND'
                values.append(v)
        if len(data.keys()) > 0:
            query = query[:-4]
    connect = mysql.connect
    cursor = connect.cursor()
    cursor.execute(
        query
    )
    answer = cursor.fetchall()
    cursor.close()
    connect.close()
    return answer


def create_user_func(_username: str, _password: str, _role: str, _name: str = None, _surname: str = None,
                     _email: str = None) -> list:
    connect = mysql.connect
    cursor = connect.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE username = %s", (_username,)
    )
    result = cursor.fetchall()

    if len(result) > 0:
        return ['Failed']
    hashed_password = hashlib.md5(_password.encode()).hexdigest()
    if _name is not None:
        if _surname is not None:
            cursor.execute(
                "INSERT INTO users(name, surname, username, email, password, role) "
                "VALUES(%s, %s, %s, %s, %s, %s)", (_name, _surname, _username, _email, hashed_password, _role)
            )
        else:
            cursor.execute(
                "INSERT INTO users(name, username, email, password, role) "
                "VALUES(%s, %s, %s, %s, %s)", (_name, _username, _email, hashed_password, _role)
            )
    else:
        cursor.execute(
            "INSERT INTO users(username, email, password, role) "
            "VALUES(%s, %s, %s, %s)", (_name, _username, _email, hashed_password, _role)
        )
    connect.commit()
    cursor.execute(
        "SELECT id FROM users WHERE username = %s", (_username,)
    )
    result = cursor.fetchone()
    cursor.close()
    connect.close()
    return ['OK', result[0]]


def login_user_func(_username: str, _role: str, _password: str) -> list:
    connect = mysql.connect
    cursor = connect.cursor()
    cursor.execute(
        "SELECT id, role, password FROM users WHERE username = %s", (_username,)
    )
    user = cursor.fetchone()
    cursor.close()
    connect.close()

    hashed_password = hashlib.md5(_password.encode()).hexdigest()
    if user[1] == _role and user[2] == hashed_password:
        return ['OK', user[0]]
    return ['Failed']


def update_user_func(data: dict) -> list:
    connect = mysql.connect
    cursor = connect.cursor()
    if 'name' in data:
        cursor.execute(
            "UPDATE users SET name = %s WHERE id = %s;", (data['name'], data['user_id'])
        )
    if 'surname' in data:
        cursor.execute(
            "UPDATE users SET surname = %s WHERE id = %s;", (data['surname'], data['user_id'])
        )
    if 'username' in data:
        cursor.execute(
            "UPDATE users SET username = %s WHERE id = %s;", (data['username'], data['user_id'])
        )
    if 'email' in data:
        cursor.execute(
            "UPDATE users SET email = %s WHERE id = %s;", (data['email'], data['user_id'])
        )
    if 'password' in data:
        hashed_password = hashlib.md5(data['password'].encode()).hexdigest()
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s;", (hashed_password, data['user_id'])
        )
    if 'role' in data:
        cursor.execute(
            "UPDATE users SET role = %s WHERE id = %s;", (data['role'], data['user_id'])
        )
    cursor.execute(
        "UPDATE users SET updated_at = %s WHERE id = %s;", (datetime.datetime.now(), data['user_id'])
    )
    connect.commit()
    cursor.close()
    connect.close()
    return ['OK', data['user_id']]


def search_user_func(data):
    query = "SELECT id, name, surname, username, email, role FROM users"
    users = search(data, query)
    answer = []
    for user_id, name, surname, username, email, role in users:
        answer.append({
            'user_id': user_id,
            'name': name,
            'surname': surname,
            'username': username,
            'email': email,
            'role': role
        })
    return ['OK', answer]


def delete_user_func(data):
    connect = mysql.connect
    cursor = connect.cursor()
    cursor.execute(
        "SELECT role FROM users WHERE id = %s", (data['user_id'],)
    )
    user = cursor.fetchone()
    if user is None or user[0] != 'admin':
        return ['Failed']
    cursor.execute(
        "delete from users where id = %s;", (data['delete_user_id'],)
    )
    connect.commit()
    cursor.close()
    connect.close()
    return ['OK']


# =====================================================================


def create_subject_func(data):
    connect = mysql.connect
    cursor = connect.cursor()
    cursor.execute(
        "SELECT role FROM users WHERE id = %s;", (data['user_id'],)
    )
    author = cursor.fetchone()
    if author[0] == 'student':
        return ['Failed']
    cursor.execute(
        "INSERT INTO subjects(title, author_id) VALUES (%s, %s);", (data['title'], data['user_id'])
    )
    connect.commit()
    cursor.execute(
        "SELECT id FROM subjects WHERE author_id = %s AND title = %s;", (data['user_id'], data['title'])
    )
    subject = cursor.fetchone()
    cursor.close()
    connect.close()
    return ['OK', subject[0]]


def update_subject_func(data):
    connect = mysql.connect
    cursor = connect.cursor()
    cursor.execute(
        "SELECT author_id FROM subjects WHERE id = %s;", (data['subject_id'],)
    )
    author = cursor.fetchone()
    if author is None or author[0] != data['user_id']:
        return ['Failed']
    cursor.execute(
        "UPDATE subjects SET title = %s, updated_at = %s WHERE id = %s;",
        (data['title'], datetime.datetime.now(), data['subject_id'])
    )
    connect.commit()
    cursor.close()
    connect.close()
    return ['OK']


def search_subject_func(data):
    query = "SELECT id, title FROM subjects"
    subjects = search(data, query)
    answer = []
    for subject_id, title in subjects:
        answer.append({
            'subject_id': subject_id,
            'title': title
        })
    return ['OK', answer]


def delete_subject_func(data):
    connect = mysql.connect
    cursor = connect.cursor()
    cursor.execute(
        "SELECT role FROM users WHERE id = %s", (data['user_id'],)
    )
    user = cursor.fetchone()
    cursor.execute(
        "SELECT author_id FROM subjects WHERE id = %s", (data['delete_subject_id'],)
    )
    author_id = cursor.fetchone()

    if user is not None and user[0] != 'admin' and author_id is None or \
            author_id is not None and author_id[0] != data['user_id']:
        return ['Failed']
    cursor.execute(
        "delete from subjects where id = %s;", (data['delete_subject_id'],)
    )
    connect.commit()
    cursor.close()
    connect.close()
    return ['OK']


# =========================================================


def create_theme_func(data):
    connect = mysql.connect
    cursor = connect.cursor()
    cursor.execute(
        "SELECT author_id FROM subjects WHERE id = %s;", (data['subject_id'],)
    )
    author = cursor.fetchone()
    if author[0] != data['user_id']:
        return ['Failed']
    insert = "INSERT INTO themes (title, subject_id"
    values = "%s, %s"
    val = [data['title'], data['subject_id']]
    if 'description' in data:
        insert += ', description'
        values += ', %s'
        val.append(data['description'])

    insert += ') VALUES (' + values + ');'
    cursor.execute(
        insert, val
    )
    connect.commit()
    cursor.execute(
        "SELECT id FROM themes WHERE subject_id = %s AND title = %s;", (data['subject_id'], data['title'])
    )
    theme = cursor.fetchone()
    return ['OK', theme[0]]


def update_theme_func(data):
    connect = mysql.connect
    cursor = connect.cursor()
    cursor.execute(
        "SELECT author_id FROM subjects WHERE id = %s;", (data['subject_id'],)
    )
    author = cursor.fetchone()
    cursor.execute(
        "SELECT subject_id FROM themes WHERE id = %s;", (data['theme_id'],)
    )
    subject = cursor.fetchone()
    if author is None or subject is None or author[0] != data['user_id'] or subject[0] != data['subject_id']:
        return ['Failed']
    if 'title' in data:
        cursor.execute(
            "UPDATE themes SET title = %s WHERE id = %s;", (data['title'], data['theme_id'])
        )
    if 'description' in data:
        cursor.execute(
            "UPDATE themes SET description = %s WHERE id = %s;", (data['description'], data['theme_id'])
        )
    cursor.execute(
        "UPDATE themes SET updated_at = %s WHERE id = %s;", (datetime.datetime.now(), data['theme_id'])
    )
    connect.commit()
    cursor.close()
    connect.close()
    return ['OK']


def search_theme_func(data):
    query = "SELECT id, subject_id, title FROM themes"
    themes = search(data, query)

    answer = []
    for theme_id, subject_id, title in themes:
        answer.append({
            'theme_id': theme_id,
            'subject_id': subject_id,
            'title': title
        })
    return ['OK', answer]


def delete_theme_func(data):
    connect = mysql.connect
    cursor = connect.cursor()
    cursor.execute(
        "SELECT role FROM users WHERE id = %s", (data['user_id'],)
    )
    user = cursor.fetchone()
    cursor.execute(
        "SELECT author_id FROM subjects WHERE id = %s", (data['subject_id'],)
    )
    author_id = cursor.fetchone()
    if user is not None and user[0] != 'admin' and author_id is None or \
            author_id is not None and author_id[0] != data['user_id']:
        return ['Failed']
    cursor.execute(
        "SELECT subject_id FROM themes WHERE id = %s", (data['delete_theme_id'],)
    )
    subject_id = cursor.fetchone()
    if subject_id is None or subject_id[0] != data['subject_id']:
        return ['Failed']
    cursor.execute(
        "delete from themes where id = %s;", (data['delete_theme_id'],)
    )
    connect.commit()
    cursor.close()
    connect.close()
    return ['OK']


if __name__ == '__main__':
    app.run(debug=True)
