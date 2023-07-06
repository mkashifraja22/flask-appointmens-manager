from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance


project_user_association = db.Table(
    'project_user_association',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='assigned_projects', lazy=True)
    users = db.relationship('User', secondary=project_user_association, backref=db.backref('projects', lazy='dynamic'))

    def __repr__(self):
        return f'<Project {self.name}>'

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    pid = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref('participants', lazy=True))

    nk_name = db.Column(db.String(100), nullable=False)
    nk_address = db.Column(db.String(200), nullable=False)
    nk_phone = db.Column(db.String(15), nullable=False)
    nk_email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Participant {self.name}>'

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    participant = db.relationship('Participant', backref=db.backref('documents', lazy=True))
    file_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Document {self.id}>'

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    next_appointment_date = db.Column(db.DateTime, nullable=True)
    next_appointment_interval = db.Column(db.Integer, nullable=True)  # Number of days or months
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    participant = db.relationship('Participant', backref=db.backref('appointments', lazy=True))

    def __repr__(self):
        return f'<Appointment {self.id}>'

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    participant = db.relationship('Participant', backref=db.backref('notes', lazy=True))

    def __repr__(self):
        return f'<Note {self.id}>'

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance


g_p_association = db.Table(
    'g_p_association',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('participant_id', db.Integer, db.ForeignKey('participant.id'))
)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='assigned_groups', lazy=True)
    participants = db.relationship('Participant', secondary=g_p_association,
                                   backref=db.backref('groups', lazy='dynamic'))

    def __repr__(self):
        return f'<Group {self.id}>'

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance
