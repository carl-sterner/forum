from flask import Flask, render_template, session, request, redirect, url_for, flash
from databas import init_db, get_user, get_all_topics, get_topic, get_posts, create_topic, create_post, get_user_by_id, update_user, create_user
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'nyckel'

with app.app_context():
    init_db()

@app.route('/')
def index():
    topics = get_all_topics()
    return render_template('index.html', topics=topics)

@app.route('/topic/<int:topic_id>')
def view_topic(topic_id):
    topic = get_topic(topic_id)
    if not topic:
        flash('Tråden hittades inte', 'error')
        return redirect(url_for('index'))
    
    posts = get_posts(topic_id)
    return render_template('topic.html', topic=topic, posts=posts)

@app.route('/topic/<int:topic_id>/post', methods=['POST'])
def create_post_route(topic_id):
    if not session.get('user_id'):
        flash('Du måste vara inloggad för att svara', 'error')
        return redirect(url_for('login'))
    
    content = request.form.get('content')
    
    if not content or len(content.strip()) == 0:
        flash('Innehåll måste anges', 'error')
        return redirect(url_for('view_topic', topic_id=topic_id))
    
    create_post(content, topic_id, session['user_id'])
    flash('Svar skickat!', 'success')
    return redirect(url_for('view_topic', topic_id=topic_id))

@app.route('/new_topic', methods=['GET', 'POST'])
def new_topic():
    if not session.get('user_id'):
        flash('Du måste vara inloggad för att skapa en tråd', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        
        if not title or len(title.strip()) == 0:
            flash('Titel måste anges', 'error')
            return render_template('new_topic.html')
        
        topic_id = create_topic(title, session['user_id'])
        flash('Tråd skapad!', 'success')
        return redirect(url_for('view_topic', topic_id=topic_id))
    
    return render_template('new_topic.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if password != password_confirm:
            flash('Lösenorden matchar inte', 'error')
            return render_template('register.html')

        if len(username.strip()) == 0 or len(password.strip()) == 0:
            flash('Användarnamn och lösenord krävs', 'error')
            return render_template('register.html')

        user_id = create_user(username, password, name, email)
        if user_id is None:
            flash('Användarnamnet är redan upptaget', 'error')
            return render_template('register.html')

        session['user_id'] = user_id
        session['username'] = username
        session['name'] = name
        flash('Registrering lyckades! Du är nu inloggad.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        flash('Du måste vara inloggad för att se profil', 'error')
        return redirect(url_for('login'))

    user = get_user_by_id(session['user_id'])

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        bio = request.form.get('bio')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if password and password != password_confirm:
            flash('Lösenorden matchar inte', 'error')
            return render_template('profile.html', user=user)

        update_user(
            user_id=session['user_id'],
            name=name,
            email=email,
            bio=bio,
            password=password if password else None
        )

        flash('Profil uppdaterad!', 'success')
        session['name'] = name
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = get_user(username)

        if user and check_password_hash(user['password'], password):
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