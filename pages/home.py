"""The home page"""
from typing import Dict, List
import flask
import time
from dash import callback, dcc, html, register_page, Output, Input, State
import dash_bootstrap_components as dbc
import sqlalchemy

import database
import gpt
import app_globals
from app_globals import MessageType
from prompts import ask_exercise, ask_title


register_page(__name__, path="/")


def options_from_settings_key(key: str) -> List[Dict[str, str]]:
    """Transform a list of names to dropdown option values"""
    return [{"label": val, "value": val} for val in app_globals.app_settings[key]]


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
    """Layout of the home page"""
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
                html.H3("Answer"),
                dbc.Form(
                    dbc.Textarea(id="exercise-answer", size="lg", style={"height": 200})
                ),
            ],
            id="exercise-main",
            style={"display": "none"},
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
        dcc.Store("timer-start-in-seconds"),
    ]


@callback(
    [
        Output("start-button", "children"),
        Output("start-button", "color"),
        Output("interval-component", "max_intervals"),
        Output("timer-start-in-seconds", "data"),
        Output("exercise-title", "children"),
        Output("exercise-description", "children"),
        Output("exercise-options", "style"),
        Output("exercise-main", "style"),
    ],
    [
        Input("start-button", "n_clicks"),
    ],
    [
        State("level-dropdown", "value"),
        State("topic-dropdown", "value"),
        State("time-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def start_exercise(n_clicks, level, topic, duration):
    """Start the exercise: show the result of the prompt and start the timer"""
    if n_clicks % 2 == 0:
        return [
            "Start",
            "primary",
            0,
            None,
            "",
            "",
            {"display": "block"},
            {"display": "none"},
        ]

    prompt = ask_exercise.format(level, topic, duration)
    messages = [
        {
            "role": "user",
            "content": prompt,
            "message_type": MessageType.INITIAL_QUESTION,
        }
    ]
    exercise = gpt.get_completion(messages)["message"]["content"]
    messages += [
        {
            "role": "assistant",
            "content": exercise,
            "message_type": MessageType.INITIAL_EXERCISE,
        }
    ]
    messages += [
        {"role": "user", "content": ask_title, "message_type": MessageType.ASK_TITLE}
    ]
    title = gpt.get_completion(messages)["message"]
    title["message_type"] = MessageType.EXERCISE_TITLE
    messages += [title]

    start_time = time.time()

    user = flask.session.get("user")
    if user is not None:
        with database.Session(database.engine) as session:
            # noinspection PyTypeChecker
            user = session.scalars(
                sqlalchemy.select(database.User).where(user["id"] == database.User.id)
            ).first()
            exercise_obj = database.save_exercise(
                session, user, title["content"], start_time
            )

            message_objs = [
                database.Message(
                    exercise=exercise_obj,
                    role=message["role"],
                    text=message["content"],
                    message_type=message["message_type"],
                )
                for message in messages
            ]
            session.add_all(message_objs)
            session.commit()

    return [
        "Done",
        "success",
        -1,
        start_time,
        title["content"],
        exercise,
        {"display": "none"},
        {"display": "block"},
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
    Output("start-button", "disabled"),
    [
        Input("level-dropdown", "value"),
        Input("topic-dropdown", "value"),
        Input("time-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def enable_start(level, topic, duration):
    """Enable the start button"""
    return level is None or topic is None or duration is None
