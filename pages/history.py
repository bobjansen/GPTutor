"""Display the exercise history"""
import datetime
from typing import Optional

import flask
from dash import dcc, html, register_page
import dash_bootstrap_components as dbc
import sqlalchemy
import database
from app_globals import MessageType

register_page(__name__)


def layout(hid: Optional[str] = None) -> dbc.Container:
    """Layout of the exercise history page"""
    print(f"{hid=}")
    user = flask.session.get("user")
    if user is None:
        return dbc.Container()

    if hid is None:
        # noinspection PyTypeChecker
        exercises = database.Session(database.engine).scalars(
            sqlalchemy.select(database.Exercise).where(
                user["id"] == database.Exercise.user_id
            )
        )
        if exercises is None:
            return dbc.Container()
        return overview(exercises)

    # noinspection PyTypeChecker
    exercise = (
        database.Session(database.engine)
        .query(database.Exercise)
        .where(user["id"] == database.Exercise.user_id)
        .where(hid == database.Exercise.id)
        .first()
    )

    if exercise is None:
        return dbc.Container()

    exercise_title = [
        message.text
        for message in exercise.messages
        if message.message_type == int(MessageType.EXERCISE_TITLE)
    ]

    exercise_body = [
        message.text
        for message in exercise.messages
        if message.message_type == MessageType.INITIAL_EXERCISE
    ]
    return dbc.Container([html.H1(exercise_title), html.P(exercise_body)])


def format_title(title):
    """Remove GPT cruft from the title"""
    title = title.replace("Title: ", "").strip()
    if title[0] == '"' and title[-1] == '"':
        title = title[1:-1]
    return title


def overview(exercises: sqlalchemy.ScalarResult) -> dbc.Container:
    """Provide a history overview"""
    exercises = exercises.fetchall()
    if len(exercises) == 0:
        return dbc.Container(
            dbc.Alert("You have not started any exercises yet"), className="m-2"
        )

    return dbc.Container(
        [
            dcc.Location(id="url", refresh=False),
            html.H1(id="param"),
            dbc.Table(
                [
                    html.Thead(
                        html.Tr([html.Th("Title"), html.Th("Timestamp")]),
                    )
                ]
                + [
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td(
                                        dcc.Link(
                                            format_title(row.title),
                                            href=f"/history/?hid={row.id}",
                                        )
                                    ),
                                    html.Td(
                                        datetime.datetime.fromtimestamp(
                                            row.start_timestamp
                                        )
                                    ),
                                ],
                            )
                            for row in exercises
                        ]
                    )
                ]
            ),
        ],
        className="m-2",
    )
