from flask import Flask, render_template, session, request, redirect, url_for, flash
from databas import init_db, get_user

app = Flask(__name__)
app.secret_key = 'nyckel'

with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = get_user(username)
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['name'] = user['name']
            flash('Inloggning lyckades!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Fel användarnamn eller lösenord', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Du har loggats ut', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)