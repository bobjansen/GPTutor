from typing import Dict, List

import flask
import time


from dash import callback, dcc, exceptions, html, register_page, Output, Input

import gpt
from prompts import ask_exercise, ask_title
import dash_bootstrap_components as dbc
import settings

register_page(__name__, path="/")


def options_from_settings_key(key: str) -> List[Dict[str, str]]:
    return [{"label": val, "value": val} for val in settings.app_settings[key]]


dropdown_level = dcc.Dropdown(
    id="level-dropdown",
    options=options_from_settings_key("levels"),
    clearable=False,
)

dropdown_topic = dcc.Dropdown(
    id="topic-dropdown",
    options=options_from_settings_key("topics"),
    clearable=False,
)

dropdown_time = dcc.Dropdown(
    id="time-dropdown",
    options=options_from_settings_key("durations"),
    clearable=False,
)

prompt_description = html.Div(id="prompt-description", style={"fontSize:": 16})
exercise_description = html.Div(id="exercise-description", style={"fontSize:": 16})


start_button = dbc.Button(
    "Start", id="start-button", color="primary", n_clicks=0, disabled=True
)
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
            id="exercise-options",
            className="m-2",
        ),
        dbc.Container(
            [
                prompt_description,
                html.Hr(),
                html.H3("", id="exercise-title"),
                exercise_description,
            ]
        ),
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
        Output("exercise-title", "children"),
        Output("exercise-description", "children"),
        Output("exercise-options", "style"),
    ],
    [
        Input("start-button", "n_clicks"),
        Input("level-dropdown", "value"),
        Input("topic-dropdown", "value"),
        Input("time-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def start_exercise(n_clicks, level, topic, duration):
    """Start the exercise: show the result of the prompt and start the timer"""
    if n_clicks % 2 == 0:
        return ["Start", "primary", 0, None, "", "", {"display": "block"}]

    prompt = ask_exercise.format(level, topic, duration)
    messages = [{"role": "user", "content": prompt}]
    exercise = gpt.get_completion(messages)["message"]["content"]
    messages += [{"role": "assistant", "content": exercise}]
    messages += [{"role": "user", "content": ask_title}]
    title = gpt.get_completion(messages)["message"]["content"]

    return [
        "Done",
        "success",
        -1,
        time.time(),
        title,
        exercise,
        {"display": "none"},
    ]


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
    [
        Output("prompt-description", "children"),
        Output("start-button", "disabled"),
    ],
    [
        Input("start-button", "n_clicks"),
        Input("level-dropdown", "value"),
        Input("topic-dropdown", "value"),
        Input("time-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def show_prompt(_, level, topic, duration):
    if level is not None and topic is not None and duration is not None:
        prompt = ask_exercise.format(level, topic, duration)

        return [prompt, False]
    return ["", True]
