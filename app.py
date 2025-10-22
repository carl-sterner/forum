from flask import Flask, render_template, session
from databas import init_db

app = Flask(__name__)
app.secret_key = 'nyckel'

with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html') #funkar inte just nu

@app.route('/logout')
def logout():
    return "logout"

if __name__ == '__main__':
    app.run(debug=True)
