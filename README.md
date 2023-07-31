# Install

Prepare the database with `python database.py`. This will ask to create a
user. Users can be created through the web app as well.

# Run

1. Copy `gptutor.example.yaml` to `gptutor.yaml`, create a Flask secret with
   something like
```python
import secrets
secrets.token_hex(32)
```
   and copy in your OpenAI API key.
2. Run the app on localhost using `python app.py gptutor.yaml`.

Initially, OpenAI limits the API to GPT 3.5, once a $1 payment has been made,
the GPT4 API becomes available.

# TODO

- Improve the prompts
- Add topics
- Improve the design
- Use local storage only for anonymous users