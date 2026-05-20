import random

QUOTES = [
    "Push harder than yesterday.",
    "Your only limit is you.",
    "Run now, shine later.",
    "Discipline beats motivation.",
    "Every mile counts.",
    "Sweat today, stronger tomorrow."
]

def get_random_quote():
    return random.choice(QUOTES)

def calculate_pace(distance, duration):
    if duration == 0:
        return 0
    return round(distance / duration, 2)