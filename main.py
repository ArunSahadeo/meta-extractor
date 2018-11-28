#!/usr/bin/env python3 -u

import re, requests, sys, urllib
from pathlib import Path
from time import sleep
try:
	from BeautifulSoup import BeautifulSoup
except ImportError:
	from bs4 import BeautifulSoup
from fake_useragent import UserAgent
ua = UserAgent()
headers = {'User-Agent': ua.random}

found_entries = []
google_base_uri = 'https://www.google.co.uk'
google_search_uri = 'https://www.google.co.uk/search?q=site%3A*PLACEHOLDER*'

outfile_path = './results.txt'

outfile = open(outfile_path, 'a')

def getMeta(meta_type, url):

    if (len(str(meta_type)) < 1):
        return

    request_site_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(request_site_page.text, 'html.parser')
    
    if meta_type == 'title':
        meta_title = soup.find('title').text
        if len(str(meta_title)) > 0:
            return meta_title

        return 'N/A'

    elif meta_type == 'description':
        meta_description = soup.find(attrs={'name': 'description'})

        if meta_description is not None and 'content' in meta_description:
            meta_description = meta_description['content']
            return meta_description

        return 'N/A'

def isNextLink(tag):
    return tag.name == 'a' and 'next' in str(tag.text).lower()

def isEmpty(structure):
    if structure:
        return False
    else:
        return True

def querySite(domain):
    print(domain)
    sleep(0.5)
    request_search_page = requests.get(domain, headers=headers)
    soup = BeautifulSoup(request_search_page.text, 'html.parser')
    results = soup.find_all(class_='g')

    if not len(results):
        print("We couldn't find any pages for this URL: %s" % (domain))
        return

    for result in results:
        url = result.find('a')['href']
        parsed_url = urllib.parse.urlparse(url)

        if len(parsed_url.query) > 0 or parsed_url.query is not None:
            query_params = urllib.parse.parse_qs(parsed_url.query)

            if isEmpty(query_params) or 'q' not in query_params:
                continue

            url = urllib.parse.parse_qs(parsed_url.query)['q'][0]

        if len(str(url)) < 1:
            continue

        sleep(0.5)

        meta_title = getMeta('title', url)
        meta_description = getMeta('description', url)

        if url is None:
            url = 'N/A'

        if meta_title is None:
            meta_title = 'N/A'

        if meta_description is None:
            meta_description = 'N/A'

        message = str("URL: %s Title: %s Description: %s") % (url, meta_title, meta_description)

        print(message, file=outfile)

    if soup.find(isNextLink) is None:
        return

    next_step_link = str(google_base_uri + soup.find(isNextLink)['href'])

    if next_step_link is not None:
        querySite(next_step_link)

domain = input('Please enter the URL you wish to query: ')

while not domain:
    domain = input('Please enter the URL you wish to query: ')

while not domain.strip():
    domain = input('Please enter the URL you wish to query: ')

domain = urllib.parse.quote_plus(domain).lower()
google_search_request = str(google_search_uri).replace('*PLACEHOLDER*', domain)
querySite(google_search_request)
