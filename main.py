"""Setup Dash and run the app"""
import flask
import sys
from typing import Dict
from dash import (
    callback,
    dcc,
    exceptions,
    html,
    page_container,
    page_registry,
    Dash,
    Output,
    Input,
)
import dash_bootstrap_components as dbc


def run(app_settings: Dict):
    """Run the app"""
    app = Dash(
        __name__,
        title="GP Tutor",
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        use_pages=True,
        update_title=None,
    )
    app.config.suppress_callback_exceptions = True
    app.server.secret_key = app_settings["flask_secret"]

    app.layout = dbc.Container(
        [
            dbc.NavbarSimple(
                [
                    dbc.NavItem(
                        dbc.NavLink(
                            page["name"],
                            id="nav-" + page["name"].lower().replace(" ", "-"),
                            href=page["relative_path"],
                        )
                    )
                    for page in page_registry.values()
                ],
                brand="GP Tutor",
            ),
            page_container,
            html.Div(
                dcc.Markdown(
                    """Made by Bob Jansen, [source](https://www.github.com/bobjansen)."""
                ),
                className="d-flex mt-5 justify-content-center",
            ),
        ],
        className="p-5",
    )
    app.run_server(debug=True)


@callback(
    [
        Output("nav-login", "style"),
        Output("nav-logout", "style"),
        Output("nav-create-account", "style"),
        Output("nav-history", "style"),
    ],
    [Input("url", "pathname")],
)
def toggle_elements_logged_in(href):
    """Toggle visibility of elements based on logged in status"""
    if href is None:
        raise exceptions.PreventUpdate
    user = flask.session.get("user")
    if user is None:
        return [
            {"display": "block"},
            {"display": "none"},
            {"display": "block"},
            {"display": "none"},
        ]
    else:
        return [
            {"display": "none"},
            {"display": "block"},
            {"display": "none"},
            {"display": "block"},
        ]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("One argument required: the location of the settings yaml file")
    else:
        import settings

        run(settings.app_settings)
