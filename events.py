import os
from flask import Flask, request, abort, url_for, redirect, session, render_template, g, flash
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Event
from datetime import *

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'events.db')

app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'complex string'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.before_first_request
def initdb():
    """TODO: CHANGE TO COMMAND LINE"""
    # Initialize Databases BEFORE any requests
    g.user = None
    db.create_all()
    print('Initialized the database.')


@app.before_request
def before_request():
    """
    Before requests, check if a user is logged in
    :return:  none
    """
    g.user = None
    if 'user_id' in session:
        g.user = User.query.filter_by(user_id=session['user_id']).first()


@app.route('/')
def home():
    """
    Main home page of the website
    :return: template either representing a user being logged in or not
    """
    # Customize UI to reflect whether a user is logged in
    if g.user:
        return render_template('home.html', title='Home', name=g.user.username, events=Event.query.order_by(Event.start_time).all())
    else:
        return render_template('home.html', name=None, title='Home', events=Event.query.order_by(Event.start_time).all())


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Allows new users to register for the site with UI checking logic
    :return: either display an error on the register page or redirect to login page
    """
    error = None
    if request.method == 'POST':
        if not request.form['user']:
            error = 'No username entered'
        elif not request.form['pass']:
            error = 'No password entered'
        elif get_user_id(request.form['user']) is not None:
            error = 'Username already taken'

        if error is None:
            print('no errors in input')
            db.session.add(
                User(request.form['user'], generate_password_hash(request.form['pass'])))
            db.session.commit()

            return redirect(url_for('login'))
        else:
            return render_template('register.html', title='Register', error=error)
    else:
        if g.user:
            return render_template('register.html', title='Register', name=g.user.username)
        else:
            return render_template('register.html', title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs the User into the site if the credentials are found
    :return: template for login page if credentials wrong, else redirect home
    """
    error = None
    if g.user:
        return redirect(url_for('home'))
    elif request.method == 'POST':
        user = User.query.filter_by(username=request.form['user']).first()
        if user is None:
            error = 'Invalid Username'
        elif not check_password_hash(user.pw_hash, request.form['pass']):
            error = 'Invalid Password'
        else:
            session['user_id'] = user.user_id
            return redirect(url_for('home'))
    return render_template('login.html', title='Log In', error=error)


@app.route('/logout')
def logout():
    """
    Logs the Current User Out and Redirects Back Home
    :return: Redirect for homepage
    """
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/createevent', methods=['GET', 'POST'])
def createevent():
    """
    Creates new event hosted by the signed in user
    :return: render template either containing errors or a successful event creation
    """
    if request.method == 'GET':
        return render_template('createevent.html', title='New Event', name=g.user.username)
    # Handles all user data entry logic and will create a new event with the logged in user hosting said event
    elif request.method == 'POST':
        if not request.form['title']:
            error = 'Please Enter a Title for this Event'
            return render_template('createevent.html', title='New Event', name=g.user.username, error=error)
        elif not request.form['start-time']:
            error = 'Please Enter a Start Time'
            return render_template('createevent.html', title='New Event', name=g.user.username, error=error)
        elif not request.form['end-time']:
            error = 'Please Enter an End Time'
            return render_template('createevent.html', title='New Event', name=g.user.username, error=error)
        else:
            # convert html response to python datetime
            startdt = datetime.strptime(request.form['start-time'], '%Y-%m-%dT%H:%M')
            enddt = datetime.strptime(request.form['end-time'], '%Y-%m-%dT%H:%M')
            # End time cannot be before start time
            if enddt < startdt:
                error = 'Start Time Cannot be After End Time'
                return render_template('createevent.html', title='New Event', name=g.user.username, error=error)
            # All entries OK
            event = Event(g.user.user_id, request.form['title'], request.form['desc'], startdt, enddt)
            db.session.add(event)
            db.session.commit()
            return render_template('createevent.html', title='New Event', name=g.user.username, error='Event Created!')


@app.route('/<event_id>')
def cancel_event(event_id):
    """
    Main Cancel Event Method/Page
    :param event_id: Event ID in question
    :return: template containing options to either confirm cancellation or go back to the home page
    """
    event = Event.query.filter_by(event_id=event_id).first_or_404()
    return render_template('cancelevent.html', title='Cancel Event', name=g.user.username, event=event)


@app.route('/<event_id>/cancel')
def cancel_event_helper(event_id):
    """
    Helper Event that handles the actual cancellation and deletion of event
    :param event_id: ID of event to be deleted
    :return: redirect back to home page
    """
    Event.query.filter_by(event_id=event_id).delete()
    db.session.commit()
    return redirect(url_for('home'))


def get_user_id(username):
    """
    Helper Method to get id from a username
    :param username: username to be looked up
    :return: user.user_id
    """
    rv = User.query.filter_by(username=username).first()
    return rv.user_id if rv else None


@app.route('/<event_id>/register')
def register_event(event_id):
    """
    Registers currently logged in user for an event
    :param event_id: Event ID to be registered for
    :return: Redirect for home
    """
    user_id = g.user.user_id
    return redirect(url_for('home'))


if __name__ == '__main__':
    print('yeet')
