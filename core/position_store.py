import json
import os


POSITIONS_FILE = "open_positions.json"


def load_positions():
    if not os.path.exists(POSITIONS_FILE):
        return {}

    with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_positions(data):
    with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def has_open_position(symbol):
    positions = load_positions()
    return symbol in positions


def add_position(symbol, position_data):
    positions = load_positions()
    positions[symbol] = position_data
    save_positions(positions)


def remove_position(symbol):
    positions = load_positions()
    if symbol in positions:
        del positions[symbol]
        save_positions(positions)