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

with open(os.path.join(script_dir, 'config.yml'), 'r') as stream:
    try:
        sources = yaml.safe_load(stream)
        product = sys.argv[2].lower()

        if len(sys.argv) == 4:
            key = sys.argv[3].lower()
            source = ' '.join(sources[coin][product][key])
        else:
            project = sys.argv[3].lower()
            key = sys.argv[4].lower()
            source = sources[coin][product][project][key]

        if not source:
            raise EmptyVariable

        print(source)
    except KeyError as e:
        sys.stderr.write(f"Error: coin {coin} not found\n")
        exit(1)
    except EmptyVariable:
        sys.stderr.write(f"Error: variable has not been set for {coin} ([{product}] {project}: {key})\n")
        exit(1)