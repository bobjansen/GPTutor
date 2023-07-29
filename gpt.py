import openai


def read_openai_key(config_path: str):
    """Read the key from the config file"""
    with open(config_path, "r") as f:
        return f.read()


def choose_model():
    """Select the model to use"""
    return "gpt-3.5-turbo"


class GPT:
    def __init__(self, config_path: str):
        openai.api_key = read_openai_key(config_path)
        self.model = choose_model()
        self.messages = []

    def get_completion(self, message):
        self.messages += [{"role": "user", "content": message}]
        response = openai.ChatCompletion.create(
            model=self.model, messages=self.messages, n=1
        )
        self.messages += [
            {
                "role": response.choices[0].message.role,
                "content": response.choices[0].message.content,
            }
        ]
        return response.choices[0]
