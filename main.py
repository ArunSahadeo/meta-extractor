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
        meta_title = soup.find('title')
        if meta_title is not None and len(str(meta_title.text)) > 0:
            return meta_title.text
        else:
            return 'N/A'

    elif meta_type == 'description':
        meta_description = soup.find(attrs={'name': 'description'})

        if meta_description['content'] is not None:
            meta_description = meta_description['content']
            return meta_description
        else:
            return 'N/A'

def isNextLink(tag):
    return tag.name == 'a' and 'next' in str(tag.text).lower()

def isEmpty(structure):
    if structure:
        return False
    else:
        return True

def querySite(domain):
    print('Now visiting ' + domain)
    sleep(3)
    request_search_page = requests.get(domain, headers=headers)
    soup = BeautifulSoup(request_search_page.text, 'html.parser')
    results = soup.find_all(class_='g')

    if request_search_page.status_code is not 200:
        print('Error: The URL you are trying to access is returning a status code of %s' % (request_search_page.status_code))
        print('This is the response we got: %s' % (request_search_page.text))
        return

    if not len(results):
        print('We couldn\'t find any pages for this URL: %s' % (domain))
        return

    for result in results:
        url = result.find('a')['href']
        parsed_url = urllib.parse.urlparse(url)

        if len(parsed_url.query) > 0 or parsed_url.query is not None:
            query_params = urllib.parse.parse_qs(parsed_url.query)

            if not isEmpty(query_params) and 'q' in query_params:
                url = urllib.parse.parse_qs(parsed_url.query)['q'][0]

        if len(str(url)) < 1:
            continue

        print('Now crawling ' + url)

        sleep(3)

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
