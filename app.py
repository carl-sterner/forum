from flask import Flask, render_template, session, request, redirect, url_for, flash
from databas import init_db, get_user, get_all_topics, get_topic, get_posts, create_topic, create_post

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