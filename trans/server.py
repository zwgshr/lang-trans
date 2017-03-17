from flask import request, Flask, render_template, session, redirect, url_for, escape
from werkzeug import secure_filename
import os

UPLOAD_FOLDER = 'temp/'
ALLOWED_EXTENSIONS = set(['lang', 'py'])

app = Flask(__name__)
app.secret_key = '123456'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 上传文件限制

users = {
    'admin@a': 'admin',
    'coc@c': 'admin',
}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def _yz_user(ses):
    if 'email' in ses and 'password' in ses:
        if ses['email'] in users and ses['password'] == users[ses['email']]:
            return True

    return False


@app.route('/')
@app.route('/index')
def index():
    if not _yz_user(session):
        return redirect(url_for('login'))
    else:
        return render_template('trans.html', name="0")


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
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('password', None)
    return redirect(url_for('index'))


@app.route('/FileUpload/Upload', methods=['POST'])
def Upload(**args):
    file = request.files['file_data']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    return 'ok'


if __name__ == "__main__":
    app.run('0.0.0.0')
