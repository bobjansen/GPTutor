"""The create account page"""
from dash import register_page
import flask
import dash_bootstrap_components as dbc

register_page(__name__)


def layout():
    """The create account page layout"""
    user = flask.session.get("user")
    if user is not None:
        return dbc.Alert("Already logged in", color="success")
