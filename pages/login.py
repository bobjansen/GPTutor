"""The login page"""
import flask
from dash import callback, dcc, exceptions, register_page, Output, Input, State
import dash_bootstrap_components as dbc
import database

register_page(__name__)


def layout():
    """The login page layout"""
    user = flask.session.get("user")
    if user is not None:
        return dbc.Form()

    return dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Label("E-mail:", html_for="username", width=1),
                    dbc.Col(
                        dbc.Input(id="email", type="text", placeholder="E-mail"),
                        width=2,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Label("Password:", html_for="password", width=1),
                    dbc.Col(
                        dbc.Input(
                            id="password", type="password", placeholder="Password"
                        ),
                        width=2,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Button("Log in", id="submit-login", color="primary")),
                ],
                className="mb-3",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Alert(
                        "Failed",
                        id="login-fail",
                        className="danger-alert",
                        color="danger",
                        class_name="mb-2",
                        style={"display": "none"},
                    ),
                    width=3,
                ),
            ),
        ],
        className="m-2",
    )


@callback(
    [Output("login-fail", "children"), Output("login-fail", "style")],
    [
        Input("submit-login", "n_clicks"),
    ],
    [
        State("email", "value"),
        State("password", "value"),
    ],
    prevent_initial_call=True,
)
def login_user(_, email, password):
    """Login a user of the login button click"""
    session = flask.session
    if email is None or password is None:
        raise exceptions.PreventUpdate
    user = database.verify_password(email, password)
    if user is not None:
        session.setdefault("user", {"username": user.username, "id": user.id})
        return [dcc.Location(pathname="/", id="login-fail"), {}]
    else:
        return ["Failed", {"display": "block"}]
