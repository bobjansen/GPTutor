import bcrypt  # scrypt can be hard to install.
import sqlite3
import sqlalchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import declarative_base, Session
from typing import Optional


DB_NAME = "gptutor.sqlite"

conn = sqlite3.connect(DB_NAME)
engine = create_engine("sqlite:///" + DB_NAME)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.Text, unique=True, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.Text, unique=True, nullable=False)
    password = sqlalchemy.Column(sqlalchemy.Text, nullable=False)


class Exercise(Base):
    __tablename__ = "exercises"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user = sqlalchemy.ForeignKey(User.id)


class Message(Base):
    __tablename__ = "message"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    exercise = sqlalchemy.ForeignKey(Exercise.id)


def create_user(username, email: str, password: str):
    salt = bcrypt.gensalt()
    pwhash = bcrypt.hashpw(bytes(password, "utf-8"), salt)
    with Session(engine) as session:
        session.add(User(username=username, email=email, password=pwhash))
        session.commit()


def verify_password(email: str, password: str) -> Optional[sqlalchemy.Row]:
    with Session(engine) as session:
        row = session.scalars(select(User).where(email == User.email)).one()
        if row is None:
            return None
        if bcrypt.checkpw(bytes(password, "utf-8"), row.password):
            return row
        return None


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    yn = input("Create a user y/n: ").lower()
    if yn == "y":
        given_username = input("Username: ")
        given_email = input("Email: ")
        given_password = input("Password: ")
        create_user(given_username, given_email, given_password)
