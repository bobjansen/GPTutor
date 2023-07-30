import flask
from dash import callback, dcc, exceptions, html, register_page, Output, Input
import time
from prompts import ask_exercise
import dash_bootstrap_components as dbc

register_page(__name__, path="/")

dropdown_level = dcc.Dropdown(
    id="level-dropdown",
    options=[
        {"label": "Easy", "value": "Easy"},
        {"label": "Medium", "value": "Medium"},
        {"label": "Hard", "value": "Hard"},
    ],
    value="Easy",
    clearable=False,
)

dropdown_topic = dcc.Dropdown(
    id="topic-dropdown",
    options=[
        {"label": "C++", "value": "C++"},
        {"label": "Calculus", "value": "Calculus"},
        {"label": "Python", "value": "Python"},
        {"label": "R", "value": "R"},
        {"label": "SQL", "value": "SQL"},
    ],
    value="Python",
    clearable=False,
)

dropdown_time = dcc.Dropdown(
    id="time-dropdown",
    options=[
        {"label": "15 minutes", "value": "15 minutes"},
        {"label": "30 minutes", "value": "30 minutes"},
        {"label": "60 minutes", "value": "60 minutes"},
    ],
    value="15 minutes",
    clearable=False,
)

prompt_description = html.Div(id="prompt-description", style={"fontSize:": 16})

start_button = dbc.Button("Start", id="start-button", color="primary", n_clicks=0)
timer = dcc.Interval(
    id="interval-component", interval=1000, max_intervals=0
)  # interval in milliseconds


def layout():
    user = flask.session.get("user")
    if user is None:
        greeting = dbc.Alert("You are not logged in", color="danger")
    else:
        greeting = html.Div(f"Welcome {user['username']}")
    return [
        dcc.Location(id="url"),
        html.Div(greeting, className="m-2"),
        html.Div(
            [
                html.H3("Create an exercise"),
                html.Label("Select Topic"),
                dropdown_topic,
                html.Div(style={"height": "20px"}),
                html.Label("Select Difficulty"),
                dropdown_level,
                html.Div(style={"height": "20px"}),
                html.Label("Select Duration"),
                dropdown_time,
                html.Div(style={"height": "20px"}),
            ],
            className="m-2",
        ),
        prompt_description,
        html.Div(style={"height": "20px"}),
        html.Div(
            [
                start_button,
                html.H1(id="stopwatch", children="00:00:00"),
                timer,
            ],
            className="d-grid gap-2 d-md-flex justify-content-md-start",
        ),
        html.Div(
            dcc.Markdown(
                """Made by Bob Jansen, [source](https://www.github.com/bobjansen)."""
            ),
            className="d-flex mt-5 justify-content-center",
        ),
        dcc.Store("timer-start-in-seconds"),
    ]


@callback(
    [Output("nav-Login", "style"), Output("nav-Logout", "style")],
    [Input("url", "pathname")],
)
def display_page(href):
    if href is None:
        raise exceptions.PreventUpdate
    user = flask.session.get("user")
    if user is None:
        return [{"display": "block"}, {"display": "none"}]
    else:
        return [{"display": "none"}, {"display": "block"}]


@callback(
    [
        Output("start-button", "children"),
        Output("start-button", "color"),
        Output("interval-component", "max_intervals"),
        Output("timer-start-in-seconds", "data"),
    ],
    [
        Input("start-button", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def toggle_timer(n_clicks):
    """Toggle the stopwatch timer"""
    if n_clicks % 2 == 0:
        return ["Start", "primary", 0, None]
    return ["Done", "success", -1, time.time()]


@callback(
    Output("stopwatch", "children"),
    [
        Input("interval-component", "n_intervals"),
        Input("timer-start-in-seconds", "data"),
    ],
    prevent_initial_call=True,
)
def update_timer(_, timer_start):
    """
    Update the timer based on the saved timer start

    The argument n_intervals is not reliable as the browser can freeze a tab if it loses focus. This causes the timer to
    stop. Also prevents the timer from drifting.
    """
    if timer_start is None:
        return "00:00:00"

    seconds = int(time.time() - timer_start)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)


@callback(
    Output("prompt-description", "children"),
    [
        Input("start-button", "n_clicks"),
        Input("level-dropdown", "value"),
        Input("topic-dropdown", "value"),
        Input("time-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def show_prompt(_, level, topic, duration):
    prompt = create_exercise_prompt(level, topic, duration)
    return prompt
