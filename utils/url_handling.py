import urllib.parse
base_url = ""

def set_base_url(url):
    global base_url
    base_url = url

def build_url(query):
    global base_url
    return base_url + '?' + urllib.parse.urlencode(query)