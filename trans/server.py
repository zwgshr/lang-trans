from flask import request, Flask, render_template, session, redirect, url_for, escape
from flask import send_from_directory, abort, send_file, make_response
from werkzeug import secure_filename
import json
import os
import trans
import io
import time

UPLOAD_FOLDER = 'temp/'
ALLOWED_EXTENSIONS = set(['lang', 'py'])

app = Flask(__name__)
app.secret_key = '123456'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 上传文件限制

GRES = {}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def _yz_user(ses):
    if 'email' in ses and 'password' in ses:
        if ses['email'] in GRES['users'] and ses['password'] == GRES['users'][ses['email']]["password"]:
            return True

    return False


@app.route('/')
@app.route('/index')
def index():
    if not _yz_user(session):
        return redirect(url_for('login'))
    else:
        return render_template('trans.html', name="0")


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    if email in GRES['users']:
        return "用户名重复"

    GRES['users'][email] = {
        "password": password,
        "reg_time": time.time()
    }
    with open("Users.json", 'w') as f:
        f.write(json.dumps(GRES['users']))
    return "注册成功"


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if _yz_user(session):
            return redirect(url_for('index'))
        return render_template("login.html")
    else:
        session['email'] = request.form['email']
        session['password'] = request.form['password']
        if _yz_user(session):
            if not os.path.isdir(UPLOAD_FOLDER + session['email']):
                os.mkdir(UPLOAD_FOLDER + session['email'])

            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('password', None)
    return redirect(url_for('index'))


@app.route('/save', methods=["POST"])
def save():
    data = json.loads(request.form['data'])
    GRES[session['email']]['edit'] = data
    return "ok"


# @app.route('/FileUpload/Upload', methods=['POST'])
# def Upload(**args):
#     file = request.files['file_data']
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(UPLOAD_FOLDER, session['email'] + "/" + filename))
#     return json.dumps({"errno": 0, "errmsg": "上传成功"})

@app.route('/upload', methods=['POST'])
def upload():
    source = json.loads(request.form['data'])

    sdata = trans.load(source)
    res = trans.parse(sdata)

    GRES[session['email']] = {}
    GRES[session['email']]['source'] = source
    GRES[session['email']]['sdata'] = sdata
    GRES[session['email']]['res'] = res

    return json.dumps(res)


@app.route('/download')
def download():
    email = session['email']
    tmp = {}
    if email in GRES:
        if 'zh_CN' in GRES[email]['sdata']:
            tmp = GRES[email]['sdata']['zh_CN']
        else:
            res = GRES[email]['res']
            for line in res:
                tmp[line['key']] = line['zh']

        if 'edit' in GRES[email]:
            for key in GRES[email]['edit']:
                tmp[key] = GRES[email]['edit'][key]
    if not tmp:
        return "无数据可下载"

    text = ""
    for key in tmp:
        text += key + "=" + tmp[key] + "\n"

    s = io.BytesIO(text.encode())
    s.seek(0)

    response = make_response(send_file(s, mimetype="text/plain", cache_timeout=0))
    response.headers["Content-Disposition"] = "attachment; filename=zh_CN.lang;"
    return response


# 读取用户信息
def init():
    with open('Users.json') as f:
        data = json.loads(f.read())
        GRES['users'] = data
        print('成功加载账号信息')


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    init()
    app.run('0.0.0.0')
