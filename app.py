from flask import Flask
from databas import init_db

app = Flask(__name__)
app.secret_key = 'nyckel'

# initiera databas
with app.app_context():
    init_db()

@app.route('/')
def index():
    return "Forum"

if __name__ == '__main__':
    app.run(debug=True)
