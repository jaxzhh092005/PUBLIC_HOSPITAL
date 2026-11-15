"""Single source of truth for the 1-5 booking process."""

STEPS = [
    {"number": 1, "label": "Specialization", "url_name": "appointments:step1"},
    {"number": 2, "label": "Date",           "url_name": "appointments:step2"},
    {"number": 3, "label": "Information",    "url_name": "appointments:step3"},
    {"number": 4, "label": "Documents",      "url_name": "appointments:step4"},
    {"number": 5, "label": "Review",         "url_name": "appointments:step5"},
]


def get_step(number):
    return next(s for s in STEPS if s["number"] == number)


def prev_url_name(number):
    return STEPS[number - 2]["url_name"] if number > 1 else "home:home"


def next_url_name(number):
    return STEPS[number]["url_name"] if number < len(STEPS) else "home:home"