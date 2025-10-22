import sqlite3

def init_db():
    conn = sqlite3.connect('forum.db')
    c = conn.cursor()
    
    # skapa users tabell
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    #skapa topics tabell
    c.execute('''CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    #skapa posts tabell
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        topic_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (topic_id) REFERENCES topics(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    #  npgra testanvändare
    users = [
        {'admin','admin', 'Admin'}
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

if __name__ == '__main__':
    init_db()
