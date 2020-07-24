import yaml
import sys 
import os

script_dir = os.path.dirname(__file__)

class EmptyVariable(Exception):
    pass

if (len(sys.argv) < 4):
    sys.stderr.write(f"Error: at least 3 arguments expected. Provided: {sys.argv[1:]}")
    exit(1)

coin = sys.argv[1].lower()
product = sys.argv[2].lower()

sources = None

with open(os.path.join(script_dir, 'config.yml'), 'r') as stream:
    try:
        sources = yaml.safe_load(stream)
    except KeyError as e:
        sys.stderr.write(f"Error: coin {coin} not found\n")
        exit(1)
    except EmptyVariable:
        sys.stderr.write(f"Error: variable has not been set for {coin} ([{product}] {project}: {key})\n")
        exit(1)

# Case 1: options (3 args)
if len(sys.argv) == 4:
    key = sys.argv[3].lower()

    try:
        print(' '.join(sources[coin][product][key]))
    except KeyError:
        print() # No options == empty output
# Case 2: configuration (4 args)
else:
    project = sys.argv[3].lower()
    key = sys.argv[4].lower()

    try:
        source = sources[coin][product][project][key]

        if not source:
            raise EmptyVariable

        print(source)

    except KeyError as e:
        print() # No options == empty output
    except EmptyVariable:
        sys.stderr.write(f"Error: variable has not been set for {coin} ([{product}] {project}: {key})\n")
        exit(1)