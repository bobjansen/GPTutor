from dash import callback, dcc, exceptions, register_page, Output, Input, State
import flask
import dash_bootstrap_components as dbc
import database

register_page(__name__)


def layout():
    user = flask.session.get("user")
    if user is not None:
        flask.session.clear()

    return dbc.Alert("Logged out", color="success")
