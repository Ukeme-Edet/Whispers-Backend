#!/usr/bin/env python3
"""
This module defines the Base class and all models in the system.
"""
import uuid

import bcrypt
from app import db
from flask_login import UserMixin


class Base(db.Model):
    """
    Base class for all models in the system.
    """

    __abstract__ = True
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class User(Base):
    """
    User model.
    """

    __tablename__ = "users"
    is_active = db.Column(db.Boolean, default=True)
    username = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=False,
    )
    inboxes = db.relationship(
        "Inbox", backref="user", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password.encode("utf-8")
        )

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def from_dict(self, data):
        for field in ["username", "email"]:
            if field in data:
                setattr(self, field, data[field])
        if "password" in data:
            self.set_password(data["password"])

    def get_id(self):
        return self.id


class Inbox(Base):
    """
    Inbox model.
    """

    __tablename__ = "inboxes"
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False
    )
    url = db.Column(db.String(128), index=True, unique=True, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=False,
    )
    messages = db.relationship(
        "Message", backref="inbox", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Inbox {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "url": f"/inboxes/{self.id}",
        }

    def from_dict(self, data):
        for field in ["name", "user_id"]:
            if field in data:
                setattr(self, field, data[field])
        if "url" in data:
            self.url = data["url"]


class Message(Base):
    """
    Message model.
    """

    __tablename__ = "messages"
    subject = db.Column(db.String(128))
    body = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)
    inbox_id = db.Column(db.String(36), db.ForeignKey("inboxes.id"))
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    def __repr__(self):
        return f"<Message {self.subject}>"

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "body": self.body,
            "read": self.read,
            "inbox_id": self.inbox_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def from_dict(self, data):
        for field in ["subject", "body", "read", "inbox_id"]:
            if field in data:
                setattr(self, field, data[field])
