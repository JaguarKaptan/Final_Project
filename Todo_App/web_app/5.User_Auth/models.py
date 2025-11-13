from app import db
from flask_login import UserMixin
import uuid
from model_helper import utc_now_naive, generate_unique_short_id
from datetime import timedelta

class CommonNotes(db.Model):
    __tablename__ = 'common_notes'

    user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), primary_key=True)
    note_id = db.Column(db.String(36), db.ForeignKey("notes.id"), primary_key=True)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    public_id = db.Column(db.String(6), unique=True, default=lambda: generate_unique_short_id())
    username = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique = True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: utc_now_naive())

    tokens = db.relationship("Token", back_populates="user", cascade="all, delete-orphan")
    security_logs = db.relationship("Security_logs", back_populates="user", cascade="all, delete-orphan")
    owned_notes = db.relationship("Notes", back_populates="owner", cascade="all, delete-orphan" )
    shared_notes = db.relationship("Notes", secondary=CommonNotes.__table__ , back_populates="shared_with")

    note_history = db.relationship("Note_History", back_populates="user", cascade="all, delete-orphan") #added new

    def __repr__(self):
        return f'<User: {self.username}, E-mail: {self.email}>'
    
    def get_id(self):
        return self.user_id
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    

class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    token = db.Column(db.String, nullable=False, unique=True)
    type = db.Column(db.String, nullable=False)  # "email_verification" / "password_reset"
    created_at = db.Column(db.DateTime, default=lambda: utc_now_naive())
    expire = db.Column(db.DateTime, default=lambda: utc_now_naive() + timedelta(hours=1))

    user = db.relationship("User", back_populates="tokens")

    # def __repr__(self):
    #     return f'<Token: {self.token}, Type: {self.type}>'
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    

class Security_logs(db.Model):
    __tablename__ = 'security_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    action = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: utc_now_naive())
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String)
    
    user = db.relationship("User", back_populates="security_logs")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        return f'<action: {self.action}, created_at: {self.created_at}>'


class Notes(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.String(36), primary_key = True, default=lambda: str(uuid.uuid4()))
    owner_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(45), nullable=False)
    content = db.Column(db.String)
    tags = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=lambda: utc_now_naive())
    updated_at = db.Column(db.DateTime, default=lambda: utc_now_naive())
    done = db.Column(db.Boolean, default=False)

    owner = db.relationship("User", back_populates="owned_notes")
    shared_with = db.relationship("User", secondary=CommonNotes.__table__ ,back_populates="shared_notes")

    #history = db.relationship("Note_History", back_populates="note") #cascade="all, delete-orphan"

class Note_History(db.Model):
    __tablename__ = 'note_history'

    id = db.Column(db.String(36), primary_key = True, default=lambda: str(uuid.uuid4()))
    note_id = db.Column(db.String(36), nullable=False) #db.ForeignKey('notes.id'), nullable=False
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False) #added new

    title = db.Column(db.String(45), nullable=False)
    action = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=lambda: utc_now_naive())

    user = db.relationship("User", back_populates="note_history")
    #note = db.relationship("Notes", back_populates="history")


