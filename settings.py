import sys
import yaml

with open(sys.argv[1], "r") as yaml_file:
    print("Loading yaml")  # How often does this actually get loaded by Dash?!
    try:
        app_settings = yaml.safe_load(yaml_file)
    except yaml.YAMLError as e:
        pass
