from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    contact = db.Column(db.String(100), nullable=True)
    society = db.Column(db.String(200), nullable=True)
    plotNo = db.Column(db.String(100), nullable=True)
    block = db.Column(db.String(10), nullable=True, default='A')
    price = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(100), nullable=True)
    date = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name or '',
            'contact': self.contact or '',
            'society': self.society or '',
            'plotNo': self.plotNo or '',
            'block': self.block or 'A',
            'price': self.price or '',
            'size': self.size or '',
            'date': self.date or '',
            'description': self.description or ''
        }

class AdminSettings(db.Model):
    __tablename__ = 'admin_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(200), nullable=False)
    
    def set_password(self, password):
        """Hash and set admin password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if admin password matches"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
