import random

def get_loc_all(text, sub):
    data = []
    try:
        while True:
            index = data[-1] if data else 0
            d = text.index(sub, index+1)
            data.append(d)
    except ValueError:
        pass
    return data

def filter_non_number(text, indexes):
    #print text
    def is_num(index):
        if index == 0:
            return False
        if index == len(text)-1:
            return True
        if text[index-1] in '0123456789' or text[index+1] in '0123456789':
            return False
        return True
    return filter(is_num, indexes)
    
def rndname(text, name):
    if random.randrange(8):
        return text
    text = text.strip()
    if not text:
        return text
    if text[-1] not in ',./;:!?':
        text += '.'
    locs = get_loc_all(text, ',')+filter_non_number(text, get_loc_all(text, '.'))
    loc = random.choice(locs) if locs else 0
    pos = [lambda: text[:loc] + ', ' + name + text[loc:] if locs else text]*len(locs)\
        + [lambda: (name+', '+text) if len(text.split()) > 6 else text, lambda: text]
    return random.choice(pos)()

if __name__ == '__main__':
    import getpass
    while True:
        input = raw_input('>>> ')
        print rndname(input, getpass.getuser())
