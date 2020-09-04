import datetime


def format_currency(amount, convert_to_dollars=True):
    if convert_to_dollars:
        amount = round(amount / 100.0, 2)

    return '{:,.2f}'.format(amount)


def current_year():
    return datetime.datetime.utcnow().year