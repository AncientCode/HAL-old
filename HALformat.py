def check_blank(input):
    if input == '' or not len(input.strip()):
        return 'Please actually type something...'
    else:
        return None

def check_for_end(input):
    return 'bye' in input.lower()

def sentence_split(input):
    end = '.?!'
    
    # Remove duplicate puntuations
    for i in end:
        z = i*2
        while z in input:
            input = input.replace(z, i)
    
    input = input.strip()
    
    strs = []
    str = ''
    
    for i in input:
        str += i
        if i in end:
            strs.append(str)
            str = ''
    if len(str):
        strs.append(str)
    return strs
