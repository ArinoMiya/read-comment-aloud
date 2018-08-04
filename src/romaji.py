# coding: utf-8
from src.urlopen import urlopen
from xml.etree.ElementTree import fromstring


def convert(text):
    url = "http://www.kawa.net/works/ajax/romanize/romanize.cgi?mode=japanese&ie=UTF-8&q="
    url += ''.join(text.split())

    req = urlopen(url, timeout=10)
    html = req.read()

    elem = fromstring(html)
    sentence = ''
    for span in elem.findall('.//span'):
        raw_word = span.get('title', '')
        word = ''
        for character in raw_word:
            if character == '/':
                break
            word += character

        if raw_word == '':
            word = span.text + ' '

        sentence += word

    return sentence
