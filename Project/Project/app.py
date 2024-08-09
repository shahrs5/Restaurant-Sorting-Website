import sqlite3, os, re
from flask import Flask, render_template, url_for, request, session, redirect


# get the path to the directory containing this script
dir_path = os.path.dirname(os.path.realpath(__file__))

# set up the Flask app instance
app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def index():

    return render_template('index.html')

# route to filter restaurants based on user input
@app.route('/search', methods=['GET', 'POST'])
def search_restaurants():
    # if the form was submitted, retrieve the search parameters

    if request.method == 'GET':
        # connect to the database
        db_path = os.path.join(dir_path, 'Database.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # build the query based on the search parameters
        c.execute("SELECT DishId, DishName FROM Dishes")
        all_dishes = c.fetchall()
        # close the database connection
        conn.close()

        print("dishes: ", all_dishes)

        return render_template('search.html', dishes=all_dishes)

    if request.method == 'POST':
        search_term = request.form['name']
        cuisine = request.form['cuisine']
        budget = request.form['budget']
        dish = request.form['dish']

        # connect to the database
        db_path = os.path.join(dir_path, 'Database.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        criteria = []
        # build the query based on the search parameters
        # query = "SELECT ID, name, rating FROM Restaurants WHERE 1=1"
        query = "SELECT ID, name, rating, RestaurantDishes.DishId, Dishes.DishName "
        query += "FROM Restaurants "
        query += "left join RestaurantDishes on RestaurantDishes.RestaurantId = Restaurants.ID "
        query += "LEFT JOIN Dishes ON Dishes.DishId = RestaurantDishes.DishId "
        query += "WHERE 1=1 "

        if search_term: 
            query += f" AND name LIKE '%{search_term}%'"
            criteria.append(f"Term: {search_term}")
        if cuisine and cuisine != 'Any':
            query += f" AND cuisine = '{cuisine}'"
            criteria.append(f"Cuisine: {cuisine}")
        if budget and budget != 'Any':
            query += f" AND budget = '{budget}'"
            criteria.append(f"Budget: {budget}")
        if dish and dish != 'Any':
            query += f" AND Dishes.DishId = {dish}"
            criteria.append(f"Dish: {dish}")

        query += " ORDER BY Rating DESC LIMIT 10"

        print("query:", query)
        # execute the query and retrieve the filtered restaurants
        c.execute(query)
        filtered_restaurants = c.fetchall()

        # close the database connection
        conn.close()

        # render the template with the filtered restaurants
        return render_template('search_results.html', restaurants=filtered_restaurants, search_term1=criteria)

    # if the form was not submitted, just display the search form
    else:
        return render_template('search.html')

#Favourite
@app.route('/favourites', methods=['GET', 'POST'])
def favourites():
    if request.method == 'POST':
        user_id = session['id']
        restaurant_id = request.form['restaurant_id']
        method_html = request.form['_method']
        
        if method_html == "POST":
            if not does_favourite_exist(user_id, restaurant_id):
                db_path = os.path.join(dir_path, 'Database.db')
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute('INSERT INTO UserFavourites (UserId, RestaurantId) VALUES (?, ?)', (user_id, restaurant_id))
                conn.commit()
                conn.close()

            # return render_template('favourite_restaurants.html')
            return get_favourite_restaurants(user_id)
        elif method_html == "DELETE":
            remove_favourite(user_id, restaurant_id)
            return get_favourite_restaurants(user_id)
    
def remove_favourite(user_id, restaurant_id):
    user_id = user_id = session['id']
  
    if does_favourite_exist(user_id, restaurant_id):
        db_path = os.path.join(dir_path, 'Database.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM UserFavourites WHERE UserId = ? AND RestaurantId = ?', (user_id, restaurant_id))
        conn.commit()
        conn.close()
    
    return render_template('favourite_restaurants.html')

def does_favourite_exist(user_id, restaurant_id):
    # print(f"In does_favourite_exist. userid: {user_id}, restid: {restaurant_id}")
    db_path = os.path.join(dir_path, 'Database.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    query = "SELECT * FROM UserFavourites WHERE UserId = ? and RestaurantId = ?"
    c.execute(query, (user_id, restaurant_id))
    favourites = c.fetchall()
    if len(favourites) > 0:
        found = True
    else:
        found = False
    conn.close()

    return found


@app.route('/favourite_restaurants', methods=['GET', 'POST'])
def favourite_restaurants():
    if request.method == 'GET':
        user_id = session['id']
        # db_path = os.path.join(dir_path, 'Database.db')
        # conn = sqlite3.connect(db_path)
        # c = conn.cursor()

        # query = "SELECT * FROM Restaurants INNER JOIN UserFavourites ON Restaurants.ID = UserFavourites.RestaurantId WHERE UserId = ?"
        # c.execute(query, (user_id,))
        # favourites = c.fetchall()
        # conn.close()

        # return render_template('favourite_restaurants.html', restaurants=favourites)
        return get_favourite_restaurants(user_id)
    
def get_favourite_restaurants(user_id):
    db_path = os.path.join(dir_path, 'Database.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    query = "SELECT * FROM Restaurants INNER JOIN UserFavourites ON Restaurants.ID = UserFavourites.RestaurantId WHERE UserId = ?"
    c.execute(query, (user_id,))
    favourites = c.fetchall()
    conn.close()

    return render_template('favourite_restaurants.html', restaurants=favourites)
    

#Login    
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        db_path = os.path.join(dir_path, 'Database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Change to fstring formatting
        cursor.execute('SELECT * FROM Users WHERE Username = ? AND Password = ?', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password!'
    return render_template('login.html', msg = msg)
 
 #Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
 
#Sign Up
@app.route('/signup', methods =['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form :
        username = request.form['username']
        password = request.form['password']

        db_path = os.path.join(dir_path, 'Database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Change to fstring formatting
        cursor.execute('SELECT * FROM Users WHERE Username = ?', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        # elif not re.match(r'[A-Za-z0-9]+', username):
        #     msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please enter a username and password'
        else:
            cursor.execute('INSERT INTO Users VALUES (NULL, ?, ?)', (username, password, ))
            conn.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('index'))
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('signup.html', msg = msg)

# route to serve static files like styles.css
@app.route('/Static/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    app.run(debug=True)