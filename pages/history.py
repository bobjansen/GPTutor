"""Display the exercise history"""
import datetime
import flask
from dash import html, register_page
import dash_bootstrap_components as dbc
import sqlalchemy
import database

register_page(__name__)


def layout():
    """Layout of the exercise history page"""
    user = flask.session.get("user")
    if user is None:
        return dbc.Container()
    # noinspection PyTypeChecker
    exercises = database.Session(database.engine).scalars(
        sqlalchemy.select(database.Exercise).where(
            user["id"] == database.Exercise.user_id
        )
    )

    if exercises is None:
        return dbc.Container()

    return dbc.Container(
        dbc.Table(
            [html.Thead(html.Tr([html.Th("Title"), html.Th("Timestamp")]))]
            + [
                html.Tr(
                    [
                        html.Td(row.title.replace("Title: ", "")),
                        html.Td(datetime.datetime.fromtimestamp(row.start_timestamp)),
                    ]
                )
                for row in exercises
            ]
        ),
        className="m-2",
    )
