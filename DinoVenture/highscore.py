import os

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'highscore.txt')

def load():
    try:
        with open(BASE_DIR) as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0

def save(high_score_value):
    with open(BASE_DIR, 'w') as f:
        f.write(str(high_score_value))