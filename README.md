# Install

Prepare the database with `python database.py`. This will ask to create a
user. Users can be created through the web app as well.

# Run

1. Copy `gptutor.example.yaml` to `gptutor.yaml`, create a Flask secret and copy 
   in your OpenAI API key
2. Run the app on localhost using 
`python app.py gptutor.yaml`

# TODO

- Improve the prompts
- Add topics
- Improve the design