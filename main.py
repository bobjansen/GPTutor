import sys
from dash import page_container, page_registry, Dash
import dash_bootstrap_components as dbc
import gpt

app = Dash(
    __name__,
    title="GP Tutor",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    update_title=None,
)
app.config.suppress_callback_exceptions = True
app.server.secret_key = "THE_SECRET_KEY"


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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("One argument required: the location of the API key")
    else:
        bot = gpt.GPT(sys.argv[1])
        app.run_server(debug=True)
