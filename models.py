from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24))
    pw_hash = db.Column(db.String(64))
    events = db.relationship('Event', backref='host')

    def __init__(self, username, pw_hash):
        self.username = username
        self.pw_hash = pw_hash

    def __repr__(self):
        return '<User{}>'.format(self.username)


class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    event_title = db.Column(db.String(100))
    event_desc = db.Column(db.String(100))
    host_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __init__(self, host_id, event_title, event_desc, start_time, end_time):
        self.host_id = host_id
        self.event_title = event_title
        self.event_desc = event_desc
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return '<Event{}>'.format(self.event_id)
