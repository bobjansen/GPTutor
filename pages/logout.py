"""The logout page. To be completed"""
from dash import register_page
import flask
import dash_bootstrap_components as dbc

register_page(__name__)


def layout():
    """The logout page layout"""
    user = flask.session.get("user")
    if user is not None:
        flask.session.clear()

    return dbc.Alert("Logged out", color="success")
