"""Database functionality for GPTutor"""
import bcrypt  # scrypt can be hard to install.
import sqlite3
import sqlalchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import declarative_base, relationship, Session
from typing import Optional


DB_NAME = "gptutor.sqlite"

conn = sqlite3.connect(DB_NAME)
engine = create_engine("sqlite:///" + DB_NAME, echo=True)

Base = declarative_base()


class User(Base):
    """Simple database User class"""

    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.Text, unique=True, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.Text, unique=True, nullable=False)
    # Specify type to silence a PyCharm warning.
    password: bytes = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    exercises = relationship("Exercise", backref="user")

    def __repr__(self) -> str:
        return f"id={self.id}: {self.email}"


class Exercise(Base):
    """Exercise holds exercise meta data"""

    __tablename__ = "exercises"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id), nullable=False
    )
    start_timestamp = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    end_timestamp = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    messages = relationship("Message", backref="exercise")

    def __repr__(self) -> str:
        return f"id={self.id}: By user: {self.user}, started at: {self.start_timestamp}"


class Message(Base):
    """Records message send and received to the GPT API"""

    __tablename__ = "message"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    exercise_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey(Exercise.id), nullable=False
    )
    role = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    message_type = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    pwhash = bcrypt.hashpw(bytes(password, "utf-8"), salt)
    return pwhash


def create_user(session: Session, username, email: str, password: str) -> User:
    """Create a user in the database, hashing with bcrypt"""
    user = User(
        username=username,
        email=email,
        password=hash_password(password),
    )
    session.add(User(username=username, email=email, password=hash_password(password)))
    session.commit()

    return user


def verify_password(email: str, password: str) -> Optional[User]:
    """Verify that the password matches the given user"""
    with Session(engine) as session:
        # Warning about sqlalchemy.exc.NoResultFound to be missing seems spurious
        # noinspection PyUnresolvedReferences
        try:
            user = session.scalars(select(User).where(email == User.email)).one()
            if bcrypt.checkpw(bytes(password, "utf-8"), user.password):
                return user
        except sqlalchemy.exc.NoResultFound:
            return None
        return None


def save_exercise(
    session: Session, user: User, title: str, start_timestamp: float
) -> Exercise:
    """Save an exercise to the database"""
    exercise = Exercise(user=user, title=title, start_timestamp=int(start_timestamp))
    session.add(exercise)
    return exercise


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    yn = input("Create a user y/n: ").lower()
    if yn == "y":
        given_username = input("Username: ")
        given_email = input("Email: ")
        given_password = input("Password: ")
        with Session(engine) as session_:
            create_user(session_, given_username, given_email, given_password)
