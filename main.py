import sys
from typing import Dict
from dash import page_container, page_registry, Dash
import dash_bootstrap_components as dbc


def run(app_settings: Dict):
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
                            id="nav-" + page["name"],
                            href=page["relative_path"],
                        )
                    )
                    for page in page_registry.values()
                ],
                brand="GP Tutor",
            ),
            page_container,
        ],
        className="p-5",
    )
    app.run_server(debug=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("One argument required: the location of the settings yaml file")
    else:
        import settings

        run(settings.app_settings)
