from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Define a list of valid usernames and passwords
users = {
    'john': 'password123',
    'jane': 'password456',
    'bob': 'password789'
}

@app.route('/')
def index():
    # If the user is already logged in, redirect to the homepage
    if 'username' in session:
        return redirect('Homepage.html')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # Get the username and password from the form
    username = request.form['username']
    password = request.form['password']

    # Check if the username and password are valid
    if username in users and users[username] == password:
        # Store the username in the session
        session['username'] = username
        # Redirect to the homepage
        redirect('Homepage.html')
