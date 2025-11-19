import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def get_connection():
    conn = sqlite3.connect('forum.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('forum.db')
    c = conn.cursor()
    
    # skapa users tabell
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        bio TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # skapa topics tabell
    c.execute('''CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # skapa posts tabell
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        topic_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (topic_id) REFERENCES topics(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # några testanvändare
    users = [
        ('holros', 'foo', 'Holger Rosell'),
        ('manfol', 'bar', 'Manna Folke'),
        ('goskor', 'baz', 'Gordon Skorpa')
    ]

    for username, password, name in users:
        try:
            c.execute('INSERT INTO users (username, password, name) VALUES (?, ?, ?)',
                     (username, password, name))
        except sqlite3.IntegrityError:
            pass  # användare finns redan
    
    conn.commit()
    conn.close()
    print("Databasen initialiserad!")

def get_all_topics():
    conn = get_connection()
    topics = conn.execute('''
        SELECT t.*, u.username, u.name 
        FROM topics t 
        JOIN users u ON t.user_id = u.id 
        ORDER BY t.created_at DESC
    ''').fetchall()
    conn.close()
    return [dict(topic) for topic in topics]

def get_topic(topic_id):
    conn = get_connection()
    topic = conn.execute('''
        SELECT t.*, u.username, u.name 
        FROM topics t 
        JOIN users u ON t.user_id = u.id 
        WHERE t.id = ?
    ''', (topic_id,)).fetchone()
    conn.close()
    return dict(topic) if topic else None

def create_topic(title, user_id):
    conn = get_connection()
    cursor = conn.execute(
        'INSERT INTO topics (title, user_id) VALUES (?, ?)',
        (title, user_id)
    )
    topic_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return topic_id

def create_post(content, topic_id, user_id):
    conn = get_connection()
    cursor = conn.execute(
        'INSERT INTO posts (content, topic_id, user_id) VALUES (?, ?, ?)',
        (content, topic_id, user_id)
    )
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return post_id

def get_posts(topic_id):
    conn = get_connection()
    posts = conn.execute('''
        SELECT p.*, u.username, u.name 
        FROM posts p 
        JOIN users u ON p.user_id = u.id 
        WHERE p.topic_id = ? 
        ORDER BY p.created_at ASC
    ''', (topic_id,)).fetchall()
    conn.close()
    return [dict(post) for post in posts]

def get_user(username):
    conn = get_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(username, password, name, email=None):
    conn = get_connection()
    try:
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        cursor = conn.execute(
            'INSERT INTO users (username, password, name, email) VALUES (?, ?, ?, ?)',
            (username, hashed, name, email)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def update_user(user_id, name=None, email=None, bio=None, password=None):
    conn = get_connection()

    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not current_user:
        conn.close()
        return False

    new_name = name if name is not None else current_user['name']
    new_email = email if email is not None else current_user['email']
    new_bio = bio if bio is not None else current_user['bio']

    if password:
        new_password = generate_password_hash(password, method='pbkdf2:sha256')
    else:
        new_password = current_user['password']

    conn.execute(
        'UPDATE users SET name = ?, email = ?, bio = ?, password = ? WHERE id = ?',
        (new_name, new_email, new_bio, new_password, user_id)
    )
    conn.commit()
    conn.close()
    return True

if __name__ == '__main__':
    init_db()