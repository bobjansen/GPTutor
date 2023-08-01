"""Load settings on import"""
from enum import IntEnum
import sys
import yaml


class MessageType(IntEnum):
    """Type of message send or received from the GPT API"""

    INITIAL_QUESTION = 1
    INITIAL_EXERCISE = 2
    ASK_TITLE = 3
    EXERCISE_TITLE = 4


try:
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as yaml_file:
            print("Loading yaml")  # How often does this actually get loaded by Dash?!
            try:
                app_settings = yaml.safe_load(yaml_file)
            except yaml.YAMLError:
                pass
except FileNotFoundError:
    pass
