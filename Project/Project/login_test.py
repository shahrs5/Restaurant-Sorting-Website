import sqlite3
from flask import Flask, render_template, request, g, session, redirect, url_for

app = Flask(__name__, template_folder='templates')
app.secret_key = 'sus'  # add a secret key to enable session
DATABASE = 'restaurant.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']
    if validate_login(username, password):
        session['username'] = username
        return redirect(url_for('Homepage.html'))
    else:
        return render_template('login.html', error='Invalid username or password')

def validate_login(username, password):
    conn = get_db()
    user = conn.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password)).fetchone()
    return user is not None

@app.route('/register', methods=['POST'])
def handle_register():
    username = request.form['username']
    password = request.form['password']
    result = register(username, password)
    if result == "User registered successfully":
        return "Registered successfully!"
    else:
        return result


def register(username, password):
    conn = get_db()
    # Check if the user already exists
    cursor = conn.execute("SELECT username FROM user WHERE username=?", (username,))
    if cursor.fetchone() is not None:
        # User already exists, return an error message
        return "User already exists"
    # User does not exist, insert the new user into the database
    conn.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    # Return success message
    return "User registered successfully"


@app.route('/favorites')
def favorites():
    if 'username' in session:
        username = session['username']
        restaurants = get_favorites(username)
        return render_template('favorites.html', restaurants=restaurants)
    else:
        return redirect(url_for('index'))

@app.route('/favorites', methods=['POST'])
def handle_favorites():
    if 'username' in session:
        username = session['username']
        restaurant = request.form['restaurant']
        add_favorite(username, restaurant)
        return redirect(url_for('favorites'))
    else:
        return redirect(url_for('index'))

def get_favorites(username):
    conn = get_db()
    favorites = conn.execute("SELECT * FROM favorites WHERE username = ?", (username,)).fetchall()
    return [f[1] for f in favorites]

def add_favorite(username, restaurant):
    conn = get_db()
    conn.execute("INSERT INTO favorites (username, restaurant) VALUES (?, ?)", (username, restaurant))
    conn.commit()

if __name__ == '__main__':
    app.run(debug=True)
