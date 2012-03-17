from datetime import date, time, datetime

_remove = '.?!'

def remove(input):
    for i in _remove:
        input = input.replace(i, '')
    return input

def is_datetime(input):
    words = remove(input).replace("'s", ' is').split()
    return ('date' in words or 'time' in words or 'datetime' in words) and 'is' in words

def answer_datetime(input):
    words = remove(input).replace("'s", ' is').split()
    if ('date' in words and 'time' in words or 'datetime' in words) and 'is' in words:
        # Datetime
        return datetime.now().strftime('It is now %H:%M:%S on %B %d, %Y.')
    elif 'date' in words and 'is' in words:
        return date.today().strftime('Today is %B %d, %Y.')
    elif 'time' in words and 'is' in words:
        return datetime.now().strftime('It is now %H:%M:%S.')
    else:
        return None
