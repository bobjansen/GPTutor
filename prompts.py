ask_exercise = """Give me a {:s} {:s} coding exercise that takes approximately {:s}.
Just ask the question, do not show any code."""


def create_exercise_prompt(level: str, topic: str, duration: str):
    return ask_exercise.format(level, topic, duration)
