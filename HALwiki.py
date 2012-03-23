from __future__ import unicode_literals
import urllib2
import difflib 
import json
from urllib import quote
import re
from urllib import quote_plus
from httplib import IncompleteRead
from Queue import Queue
from threading import Thread

from HALformat import sentence_split
from HALapi import HALcannotHandle

wpformat = 'http://en.wikipedia.org/w/api.php?format=json&action=query&titles=%s&prop=revisions&rvprop=content&redirects'
wtformat = 'http://en.wiktionary.org/w/api.php?format=json&action=query&titles=%s&prop=revisions&rvprop=content&redirects'
header = {}
delete = ['a', 'the']
relist = [(re.compile(r'\[\[Image\:.*?\]\]', re.S), ''),
          (re.compile(r'\[\[File\:.*?\]\]', re.S), ''),
          #(re.compile(r'\[\[[A-Za-z0-9 _#\(\):]*?\|([A-Za-z0-9 _\(\):\']*?)\]\]'), lambda m: m.group(1)),
          (re.compile(r'\[\[([^\]\|]+?)\]\]'), lambda m: m.group(1)),
          (re.compile(r'\[\[[^\|]*?\|([^\]]*?)\]\]'), lambda m: m.group(1)),
          #(re.compile(r'\[\[([A-Za-z0-9 _]+?)\]\]'), lambda m: m.group(1)),
          (re.compile(r"(?P<name>'{2,5})(.*?)(?P=name)"), lambda m: m.group(2)),
          (re.compile(r"<ref[^>]*?>[^<]*?<\/ref>", re.S), ''),
          (re.compile(r"<ref.*?/>", re.S), ''),
          (re.compile(r"<ref[^>]*?>.*", re.S), ''),
          (re.compile(r"[,;]?\s*{{.*?}}\s*[,;]?", re.S), ''),
          (re.compile(r"{{.*", re.S), ''),
          (re.compile(r"\s*\(\)\s*"), ' '),
          (re.compile(r"<[^>]*?>"), ''),
          (re.compile(r'<!--.*?-->', re.S), '')]

resentence = re.compile('(\. |^|!|\?)([A-Z][^;\.<>@\^&/\[\]]*(\.|!|\?) )', re.M)
recomment = re.compile(r'<!--.*?-->', re.S)
relink = re.compile(r'\*\s*\[\[([^\]\|]+?)\]\]')

web_cache = {}

def init():
    if not header:
        from HALBot import HAL
        header['User-Agent'] = 'HAL/%s'%HAL.version

def check(input):
    return 'what' in input and 'is' in input or "what's" in input

def answer(input):
    text = re.search('what is ([\w ]+)', input.replace("what's", 'what is')).group(1)
    for i in delete:
        text = text.replace(i, '')
    text = text.strip()
    handlers = [wikipedia]
    for handler in handlers:
        a = handler(text)
        if a is not None:
            return a
    raise HALcannotHandle

def most_relavent(list, to):
   #print list
   #print
   diff = difflib.SequenceMatcher(a=to.lower())
   num = re.compile('[0-9]')
   data = [(i, (diff.set_seq2(i.lower()), diff.ratio())[1]+(0.025 if num.search(i) else 0)) for i in list]
   #print data
   #print
   #print max(data, key=lambda a: a[1])[0]
   #print
   return max(data, key=lambda a: a[1])[0] 

def disambig(page):
    return relink.search(page).group(1)

def get_wikipedia_page(name):
    url = wpformat%quote(name)
    req = urllib2.Request(url, headers=header)
    resp = json.loads(urllib2.urlopen(req, timeout=5).read())
    page = resp['query']['pages'].items()[0][1]
    if 'missing' in page or 'invalid' in page:
        return None
    content = page['revisions'][0]['*']
    title = page['title']
    l = content.lower()
    #if 'did you mean' in l:
    #   return None
    #if 'related searches' in l:
    #    return None
    #if 'commonly refers to:' in l:
    #    return None
    #if 'may refer to:' in l:
    #    return None
    if '{{disambig}}' in l or '{{disambiguation}}' in l:
        return title, get_wikipedia_page(disambig(content))[1]
    return title, recomment.sub('', content).replace('{{pi}}', 'pi')

def clean_wikipedia(text):
    for re, subst in relist:
        text = re.sub(subst, text)
        #print re.pattern, subst, text.encode('mbcs', 'replace')
    return text.replace('&nbsp;', ' ')

def cached_fetch_wiki(title):
    try:
        return title, web_cache[title]
    except KeyError:
        real, data = get_wikipedia_page(title)
        web_cache[title] = data
        if real != title:
            web_cache[real] = data
        return real, data

def sentence_split(text):
    sentence_ = resentence.split(text)
    sentence = []
    end = ':,!.?'
    for i in sentence_:
        #print i
        if not i:
            continue
        if i and i[0] in end and sentence and sentence[-1][-1] not in end:
            sentence[-1] = (sentence[-1]+i).strip()
            continue
        sentence.append(i.strip())
    #print sentence
    return sentence

def wikipedia(key):
    bing = urllib2.urlopen('http://www.bing.com/search?q=%s'%quote_plus(key+' wikipedia')).read()
    #result = re.findall('http://en.wikipedia.org/wiki/([^"#]+?)"', bing)[:2]
    result = re.findall('http://en.wikipedia.org/wiki/([^"#]+?)"', bing)
    if not result:
        return None
    result = result[0].replace('_', ' ')
    #print result
    pages = {}
    #for page in result:
    for page in [result]:
        head = None
        buf = ''
        a = cached_fetch_wiki(page)
        if a is None:
            continue
        page, p = a
        print page
        if p is None:
            continue
        for line in p.split('\n'):
            if line and line[0] == '=':
                if head is not None:
                    id = '%s %s'%(page, head)
                else:
                    id = page
                pages[id] = buf
                head = line.replace('=', '').strip()
                buf = ''
            elif line and line[0] in '|<{}[]~!@#$%^&*()_+=-\\`/:;.,<>?':
                continue
            else:
                buf += line + '\n'
        if head is not None:
            id = '%s %s'%(page, head)
        else:
            id = page
        pages[id] = buf
    if not pages:
        return None
    selected = most_relavent(pages.keys(), key)
    print 'Selected:', selected
    # page = clean_wikipedia(pages[selected])
    # sentences = [i for i in sentence_split(page) if i]
    # return ''.join(sentences)
    content = pages[selected]
    firstline = ''
    for line in content.split('\n'):
        if not line:
            continue
        if line[0] in ' |<{}[]~!@#$%^&*()_+=-\\`/:;.,<>?':
            continue
        if line[-1] in ':':
            continue
        firstline = line
        break
    sentences = sentence_split(clean_wikipedia(firstline))
    #sentences = resentence.split(clean_wikipedia(firstline))
    sentences = [i for i in sentences if i and i[0] != '.']
    str = ' '.join(sentences[:2]).strip()
    if str and str[-1] not in '!.,?:':
        str += '.'
    return str
    #return str(sentences)

def get_most_relevant_subsection(pagetitle, subsection):
    diff = difflib.SequenceMatcher()
    diff.set_seq1(pagetitle)
    diff.set_seq2(subsection)
    diff.ratio()
    ratio = diff.ratio()
    print ratio
    if ratio > 0.25:
        if re.sub("\D", ', ' , pagetitle).replace(',', ' ').strip() == re.sub("\D", ', ' , subsection).replace(',', ' ').strip():
            ratio = ratio + 0.075
        else:
            print ratio

if __name__ == '__main__':
    while True:
        print wikipedia(raw_input('--> ')).encode('mbcs', 'replace')
        print
