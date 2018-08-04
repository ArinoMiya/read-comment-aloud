# coding: utf-8
from urllib.parse import urlparse
import urllib.request


def urlopen(url, timeout=2):
    p = urlparse(url)
    query = urllib.parse.quote_plus(p.query, safe='=&')
    pre_params = ';' if p.params else ''
    pre_query = '?' if p.query else ''
    pre_fragment = '#' if p.fragment else ''
    url = f'{p.scheme}://{p.netloc}{p.path}{pre_params}{p.params}{pre_query}{query}{pre_fragment}{p.fragment}'

    req = urllib.request.urlopen(url, timeout=timeout)
    return req
