import os
import bcrypt
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


# DB URI import for local workspace
from os import path
if path.exists('env.py'):
    import env

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)


# Index
@app.route('/')
def home():
    return render_template('index.html', page_title='Home')


# User Interface
@app.route('/user_interface')
def user_interface():
    if 'email' in session:
        user = mongo.db.users.find_one({'email': session['email']})
        briefs = mongo.db.briefs.find({'email': session['email']})
        creatives = mongo.db.creatives.find({'email': session['email']})
        return render_template('userInterface.html', user=user, briefs=briefs, creatives=creatives, page_title='User Interface')

    return render_template('login.html', page_title='Login')


# Login
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'email': request.form['email']})

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['email'] = request.form['email']
            return redirect(url_for('user_interface'))

    return 'Invalid email/password combination'


# Logout
@app.route('/logout')
def logout():
    session.clear()

    return render_template('index.html', page_title='Home')


# Register
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email': request.form['email']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'email': request.form['email'],
                          'first_name': request.form.get('first_name'),
                          'last_name': request.form.get('last_name'),
                          'email': request.form.get('email'),
                          'phone': request.form.get('phone'),
                          'city': request.form.get('city'),
                          'country': request.form.get('country'),
                          'password': hashpass})
            session['email'] = request.form['email']
            return redirect(url_for('user_interface'))

        return 'That email already exists!'

    return render_template('register.html')


# Update user
@app.route('/update_user', methods=["POST"])
def update_user():
    users = mongo.db.users
    users.update({'email': session['email']},
                 {
                 'first_name': request.form.get('first_name'),
                 'last_name': request.form.get('last_name'),
                 'phone': request.form.get('phone'),
                 'city': request.form.get('city'),
                 'country': request.form.get('country')
    })
    return redirect(url_for('user_interface'))


# Delete user
@app.route('/delete_user/<user_id>')
def delete_user(user_id):
    mongo.db.users.remove({'_id': ObjectId(user_id)})
    return redirect(url_for('home'))

"""
# Register Creative
@app.route('/register_creative', methods=['POST', 'GET'])
def register_creative():
    if request.method == 'POST':
        users = mongo.db.users
        creatives = mongo.db.creatives
        existing_user = users.find_one({'email': request.form['email']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'email': request.form['email'],
                          'first_name': request.form.get('first_name'),
                          'last_name': request.form.get('last_name'),
                          'email': request.form.get('email'),
                          'phone': request.form.get('phone'),
                          'city': request.form.get('city'),
                          'country': request.form.get('country'),
                          'password': hashpass})
            creatives.insert({'skills': request.form['skills'],
                              'hourly_rate': request.form['hourly_rate'],
                              'description': request.form['description']})
            session['email'] = request.form['email']
            return redirect(url_for('user_interface'))

        return 'That email already exists!'

    return render_template('register_creative.html')
"""
"""
# Register Client
@app.route('/register_client', methods=['POST', 'GET'])
def register_client():
    if request.method == 'POST':
        users = mongo.db.users
        clients = mongo.db.clients
        existing_user = users.find_one({'email': request.form['email']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'email': request.form['email'],
                          'first_name': request.form.get('first_name'),
                          'last_name': request.form.get('last_name'),
                          'email': request.form.get('email'),
                          'password': hashpass})
            clients.insert({'company_name': request.form['company_name'],
                            'phone': request.form.get('phone'),
                            'address': request.form['address'],
                            'city': request.form.get('city'),
                            'country': request.form.get('country'),
                            'vat_id': request.form['vat_id']})
            session['email'] = request.form['email']
            return redirect(url_for('user_interface'))

        return 'That email already exists!'

    return render_template('register_client.html')
"""

# Get Creatives
@app.route('/get_creatives')
def get_creatives():
    return render_template("creatives.html",
                           creatives=mongo.db.creatives.find())


# Contact creative
@app.route('/contact_creative/<creative_id>')
def contact_creative(creative_id):
    the_creative = mongo.db.creatives.find_one({"_id": ObjectId(creative_id)})
    return render_template('contactCreative.html', creative=the_creative)


# Create creative
@app.route('/create_creative')
def create_creative():
    user = mongo.db.users.find_one({'email': session['email']})
    return render_template('createCreative.html', user=user)


# Insert creative
@app.route('/insert_creative', methods=['POST'])
def insert_creative():
    creatives = mongo.db.creatives
    creatives.insert_one(request.form.to_dict())
    return redirect(url_for('user_interface'))


# Edit creative
@app.route('/edit_user/<creative_id>')
def edit_creative(creative_id):
    the_creative = mongo.db.creatives.find_one({"_id": ObjectId(creative_id)})
    return render_template('editCreative.html', creative=the_creative)


# Update creative
@app.route('/update_creative/<creative_id>', methods=["POST"])
def update_creative(creative_id):
    creatives = mongo.db.creatives
    creatives.update({'_id': ObjectId(creative_id)},
                     {
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'city': request.form.get('city'),
        'country': request.form.get('country'),
        'skills': request.form.get('skills'),
        'hourly_rate': request.form.get('hourly_rate'),
        'description': request.form.get('description')
    })
    return redirect(url_for('get_creatives'))


# Delete creative
@app.route('/delete_creative/<creative_id>')
def delete_creative(creative_id):
    mongo.db.creatives.remove({'_id': ObjectId(creative_id)})
    return redirect(url_for('get_creatives'))


# Get briefs
@app.route('/get_briefs')
def get_briefs():
    return render_template("briefs.html",
                           briefs=mongo.db.briefs.find())


# Contact employer
@app.route('/contact_employer/<brief_id>')
def contact_employer(brief_id):
    the_brief = mongo.db.briefs.find_one({"_id": ObjectId(brief_id)})
    return render_template('contactEmployer.html', brief=the_brief)


# Create brief
@app.route('/create_brief')
def create_brief():
    user = mongo.db.users.find_one({'email': session['email']})
    return render_template('createBrief.html', user=user)


# Insert brief
@app.route('/insert_brief', methods=['POST'])
def insert_brief():
    briefs = mongo.db.briefs
    briefs.insert_one(request.form.to_dict())
    return redirect(url_for('user_interface'))


# Edit brief
@app.route('/edit_brief/<brief_id>')
def edit_brief(brief_id):
    the_brief = mongo.db.briefs.find_one({"_id": ObjectId(brief_id)})
    return render_template('editBrief.html', brief=the_brief)


# Update brief
@app.route('/update_brief/<brief_id>', methods=["POST"])
def update_brief(brief_id):
    briefs = mongo.db.briefs
    briefs.update({'_id': ObjectId(brief_id)},
                     {
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'email': request.form.get('email'),
        'city': request.form.get('city'),
        'country': request.form.get('country'),
        'company_name': request.form.get('company_name'),
        'title': request.form.get('title'),
        'hours': request.form.get('hours'),
        'duration': request.form.get('duration'),
        'required_skills': request.form.get('required_skills'),
        'preferred_skills': request.form.get('preferred_skills'),
        'budget': request.form.get('budget'),
        'description': request.form.get('description')
    })
    return redirect(url_for('get_briefs'))


# Delete brief
@app.route('/delete_brief/<brief_id>')
def delete_brief(brief_id):
    mongo.db.briefs.remove({'_id': ObjectId(brief_id)})
    return redirect(url_for('get_briefs'))


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
