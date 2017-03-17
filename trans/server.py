from flask import request, Flask, render_template, session, redirect, url_for, escape

app = Flask(__name__)
app.secret_key = '123456'

users = {
    'admin@a': 'admin',
    'coc@c': 'admin',
}


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
        return 'Logged in as %s' % escape(session['email'])


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


if __name__ == "__main__":
    app.run('0.0.0.0')
