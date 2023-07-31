"""The create account page"""
from dash import register_page
import flask
from dash import callback, dcc, exceptions, Output, Input, State
import dash_bootstrap_components as dbc
import database

register_page(__name__)


def layout():
    """The create account page layout"""
    user = flask.session.get("user")
    if user is not None:
        return dbc.Alert("Already logged in", color="success")

    return dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Label("Username:", html_for="username-create", width=1),
                    dbc.Col(
                        dbc.Input(
                            id="username-create", type="text", placeholder="Username"
                        ),
                        width=2,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Label("E-mail:", html_for="email-create", width=1),
                    dbc.Col(
                        dbc.Input(id="email-create", type="text", placeholder="E-mail"),
                        width=2,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Label("Password:", html_for="password-1", width=1),
                    dbc.Col(
                        dbc.Input(
                            id="password-1", type="password", placeholder="Password"
                        ),
                        width=2,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Label("Password (repeat):", html_for="password-2", width=1),
                    dbc.Col(
                        dbc.Input(
                            id="password-2", type="password", placeholder="Password"
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
                        "",
                        id="message",
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
    [Output("message", "children"), Output("message", "style")],
    [
        Input("submit-login", "n_clicks"),
    ],
    [
        State("username-create", "value"),
        State("email-create", "value"),
        State("password-1", "value"),
        State("password-2", "value"),
    ],
    prevent_initial_call=True,
)
def create_user(_, username, email, password1, password2):
    """Login a user of the login button click"""
    if username is None or email is None or password1 is None or password2 is None:
        raise exceptions.PreventUpdate
    if password1 != password2:
        return ["Passwords don't match", {"display": "block"}]

    with database.Session(database.engine) as session:
        # noinspection PyTypeChecker
        if (
            session.query(database.User)
            .where(username == database.User.username)
            .count()
            > 0
        ):
            return ["Username exists", {"display": "block"}]

        # noinspection PyTypeChecker
        if session.query(database.User).where(email == database.User.email).count() > 0:
            return ["E-mail address already used", {"display": "block"}]

        user = database.create_user(session, username, email, password1)

        if user is not None:
            flask.session.setdefault("user", {"username": user.username, "id": user.id})
            return [dcc.Location(pathname="/", id="login-fail"), {}]

    return ["Failed", {"display": "block"}]
