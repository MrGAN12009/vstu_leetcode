from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import http.client
import json
import sqlite3
import time
import subprocess
import urllib
conn = http.client.HTTPConnection("ifconfig.me")
conn.request("GET", "/ip")
print(conn.getresponse().read())
keys = ['1']



#sql
db = sqlite3.connect("db.db")
sql = db.cursor()
sql.execute("""
CREATE TABLE IF NOT EXISTS users(
username VARCHAR(45),
password VARCHAR(20))""")
sql.execute("""
CREATE TABLE IF NOT EXISTS works(
username VARCHAR(45),
title VARCHAR(45),
forTeacher VARCHAR(45),
course INT,
predmet VARCHAR(45),
isFree BOOLEAN,
grade INT,
text TEXT)""")
db.commit()


def login(username, password):
    sql.execute(f"SELECT password FROM users WHERE username = '{username}' and password = '{password}'")
    if sql.fetchone() == None:
        return False
    return True


def register(username, password, key):
    if key not in keys:
        return False
    sql.execute(f"SELECT username FROM users WHERE username = '{username}'")
    if sql.fetchone() == None:
        sql.execute(f"INSERT INTO users (username, password) VALUES('{username}', '{password}')")
        db.commit()
        return True
    return False


def freeWorks():
    sql.execute('SELECT * FROM works')
    data = []
    for i in sql.fetchall():
        data_json = {}
        data_json['username'] = i[0]
        data_json['title'] = i[1]
        data_json['forTeacher'] = i[2]
        data_json['course'] = i[3]
        data_json['predmet'] = i[4]
        data_json['isFree'] = i[5]
        data_json['grade'] = i[6]
        data_json['text'] = i[7]
        data.append(data_json)
    return data


#('username1', 'title1', 'forteacher1', 1, 'prednet1', 1, 91, 'tttetxtitle1')
def params(forTeacher = '*', course = '*', predmet = '*', isFree = '*', grade = '*'):
    sql.execute(f"SELECT * FROM works")
    arr = sql.fetchall()
    ret = []
    for i in arr:
        if forTeacher != '*':
            if i[2] == forTeacher:
                pass
            else:
                break
        if course != '*':
            if i[3] == course:
                pass
            else:
                break
        if predmet != '*':
            if i[4] == predmet:
                pass
            else:
                break
        if isFree != '*':
            if i[5] == isFree:
                pass
            else:
                break
        if grade != '*':
            if i[6] == grade:
                pass
            else:
                break
        ret.append(i)
    return ret


def oneWork(username, title):
    sql.execute(f"SELECT * FROM works WHERE username = '{username}' and title = '{title}'")
    return sql.fetchone()


 # data = {'username', 'title', 'forTeacher', 'course', 'predmet', 'isFree', 'grade', 'text'}
def new_work(username, title, forTeacher, course, predmet, isFree, grade, text):
    try:
        sql.execute(f"INSERT INTO works(username, title, forTeacher, course, predmet, isFree, grade, text) VALUES('{username}', '{title}', '{forTeacher}', '{course}', '{predmet}', '{isFree}', '{grade}', '{text}')")
    except BaseException:
        return False
    else:
        db.commit()
        return True


#jwt
# Секретный ключ для подписи токенов
SECRET_KEY = 'piska_mamonta_ebiot_tvoyu_mamu'

def create_token(user_id):
    # Определение полезной нагрузки токена
    payload = {'user_id': user_id}
    # Создание токена
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    try:
        # Расшифровка токена
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # Токен истёк
        return None
    except jwt.InvalidTokenError:
        # Невалидный токен
        return None



#http
class HttpGetHandler(BaseHTTPRequestHandler):
    """Обработчик с реализованным методом do_GET."""

    def do_GET(self):
        # Разбор пути запроса
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        if path == '/main':
            authorization_token = self.headers.get('Authorization')
            authorization_name = self.headers.get('username')
            if authorization_token and decode_token(authorization_token)['user_id'] == authorization_name:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response = str.encode('1')
                self.wfile.write(response)
            else:
                self.send_response(410)
                #410 = no jwt token
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'')

        elif path == '/free_works':
            authorization_token = self.headers.get('Authorization')
            authorization_name = self.headers.get('username')
            if authorization_token and decode_token(authorization_token)['user_id'] == authorization_name:
                response = {
                    "status": "success",
                    "data": freeWorks()
                }
                response_json = json.dumps(response)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_json.encode('utf-8'))
            else:
                self.send_response(410)
                #410 = no jwt token
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'')


        elif path == '/params':
            authorization_token = self.headers.get('Authorization')
            authorization_name = self.headers.get('username')
            if authorization_token and decode_token(authorization_token)['user_id'] == authorization_name:
                response = {
                    "status": "success",
                    "data": params(self.headers.get('forTeacher'), self.headers.get('course'), self.headers.get('predmet'), self.headers.get('isFree'), self.headers.get('grade'))
                }
                response_json = json.dumps(response)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_json.encode('utf-8'))
            else:
                self.send_response(410)
                #410 = no jwt token
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'')


        elif path == '/python':
            with open('script.py', 'w') as f:
                f.write(self.headers.get('code'))
            start_time = time.time()
            ######################
            # Запуск второго скрипта
            process = subprocess.Popen(
                ['python3', 'script.py'],  # Команда для запуска скрипта
                stdout=subprocess.PIPE,  # Перехватываем стандартный вывод
                stderr=subprocess.PIPE,  # Перехватываем ошибки
                text=True  # Используем текстовый режим для удобного чтения
            )

            # Чтение вывода в реальном времени
            response = ''
            response += time.time() - start_time + "|"
            for line in process.stdout:
                response += line.strip()

            # Ожидание завершения процесса
            process.wait()

            # Если нужно также вывести ошибки
            stderr_output = process.stderr.read()
            if stderr_output:
                response += stderr_output


            self.send_response(410)
            #410 = no jwt token
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))


    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        json_data = json.loads(post_data)
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path


        if path == '/login':
            if login(json_data['username'], json_data['password']) == True:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response = create_token(json_data['username'])
                self.wfile.write(response.encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response = "Пошёл нахуй отсюда"
                self.wfile.write(response.encode('utf-8'))

        #data = {'username': username, 'password': password, 'access_key': access_key}
        elif path == '/register':
            if register(json_data['username'], json_data['password'], json_data['access_key']) == True:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response = 'sex'
                self.wfile.write(response.encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response = "Пошёл нахуй отсюда"
                self.wfile.write(response.encode('utf-8'))


        # data = {'username', 'title', 'forTeacher', 'course', 'predmet', 'isFree', 'grade', 'text'}
        elif path == '/new_work':
            authorization_token = self.headers.get('Authorization')
            authorization_name = self.headers.get('username')
            if authorization_token and decode_token(authorization_token)['user_id'] == authorization_name:
                if new_work(json_data['username'], json_data['title'], json_data['forTeacher'], json_data['course'], json_data['predmet'], json_data['isFree'], json_data['grade'], json_data['text']) == True:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    response = 'sex'
                    self.wfile.write(response.encode('utf-8'))
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    response = "Пошёл нахуй отсюда"
                    self.wfile.write(response.encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response = "Пошёл нахуй отсюда"
                self.wfile.write(response.encode('utf-8'))




print("Starting server on port 8000...")
server_address = ('', 8000)
httpd = HTTPServer(server_address, HttpGetHandler)
httpd.serve_forever()
