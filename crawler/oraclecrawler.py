
from bs4 import BeautifulSoup
from bs4 import Tag,NavigableString,Comment
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re
import pysolr
import http.client
import json
import sys
import posixpath
from urllib.parse import urlparse

def resolveComponents(url):
    parsed = urlparse.urlparse(url)
    new_path = posixpath.normpath(parsed.path)
    if parsed.path.endswith('/'):
        # Compensate for issue1707768
        new_path += '/'
    cleaned = parsed._replace(path=new_path)
    return cleaned.geturl()

connection = http.client.HTTPConnection("ec2-34-214-75-67.us-west-2.compute.amazonaws.com",8983)
headers = {'Content-type': 'application/json'}
solr = pysolr.Solr('//http://ec2-34-214-75-67.us-west-2.compute.amazonaws.com/:8983/solr/wikiru/', timeout=10)
new_urls = deque(['https://docs.oracle.com/javase/tutorial/'])
java_base_url = '/javase/tutorial/'
processed_urls = set()
f = open("java.txt")
keywords = f.readlines()
f.close()
javakeywords = [line.strip() for line in keywords]
#print(' '.join(javakeywords))
while len(new_urls):
    url = new_urls.popleft()
    processed_urls.add(url)
    parts = urlsplit(url)
    base_url = "{0.scheme}://{0.netloc}".format(parts)
    path = url[:url.rfind('/')+1] if '/' in parts.path else url
    print("Processing %s" % url)
    try:
        response = requests.get(url)
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
        continue

    soup = BeautifulSoup(response.text,"html.parser")

    alinks = soup.find('body')
    try:
        unwanted = alinks.find_all("div", {"id": "BreadCrumbs"})
        for a in unwanted:
            a.extract()

        unwanted = alinks.find_all("div", {"class": "NavBit"})
        for a in unwanted:
            a.extract()

        unwanted = alinks.find_all("div", {"id": "Footer"})
        for a in unwanted:
            a.extract()


        for anchor in alinks.find_all("a"):
            link = anchor.attrs["href"] if "href" in anchor.attrs else ''
            if link.startswith('/'):
                link = base_url + link
            elif not link.startswith('http'):
                link = path + link
            if "/./" in link or "/../" in link:
                link = resolveComponents(link)
            if not link in new_urls and not link in processed_urls and ( java_base_url in link ) and "https://en.wikibooks.org/wiki/Java_Programming/Collection_Classes" not in link:
                new_urls.append(link)

    except:
        continue

    result = soup.find('div[class*="MainFlow"]')

    if result is None:
        result = soup.find('div[id*="MainFlow"]')

    if result is None:
        result = soup.find("div", { "id" : "MainFlow" })

    if result is None:
        result = soup.find("div", { "class" : "MainFlow_wide" })

    if result is None:
        result = soup.find("div", { "class" : "MainFlow_wide" })

    if result is None:
        print("Mainflow not found")
        continue


    
    unwanted = result.find_all("div", {"id": "TopBar"})
    for a in unwanted:
        a.extract()

    unwanted = result.find_all("div", {"id": "RightBar"})
    for a in unwanted:
        a.extract()

    unwanted = result.find_all("div", {"id": "Footer"})
    for a in unwanted:
        a.extract()

    unwanted = result.find_all("div", {"id": "BreadCrumbs"})
    for a in unwanted:
        a.extract()

    unwanted = result.find_all("div", {"class": "NavBit"})
    for a in unwanted:
        a.extract()

    unwanted = result.find_all("div", {"class": "Banner"})
    for a in unwanted:
        a.extract()

    unwanted = result.find_all("div", {"class": "NavBit"})
    for a in unwanted:
        a.extract() 

    try:
        heading = soup.find("div", {"id": "PageTitle"})
        heading = heading.text
        heading = heading.replace("/"," ")
        heading = heading.replace(" "," ")
    except:
        heading = soup.find("h1")
        heading = heading.text
        heading = heading.replace("/"," ")
        heading = heading.replace(" "," ")

    #print(heading)
    result = soup.find("div", {"id": "PageContent"})
    filecontent = ''
    i = 0
    file = open("data/"+heading+".txt","a+")
    
    head = result.findChildren()[0]
    filecontent=''
    subheading=None
    while head is not None:
        if head.name != "h2":
            if isinstance(head, NavigableString):
                filecontent+=head
            if isinstance(head, Tag):
                filecontent+=head.get_text()
        else:
            try:
                subheading = head.contents[0].text
            except:
                subheading = "Introduction"
            if subheading is None:
                subheading = "Introduction"
            commonkeywords =  set(javakeywords) & set(filecontent.split(' '))
            doc = {'add': {'doc': {'heading': heading, 'subheading': subheading, 'url' : url, 'content' : filecontent, 'keywords' : ' '.join(commonkeywords)  }, 'boost': 1, 'overwrite': False, 'commitWithin': 1000}}
            json_doc = json.dumps(doc)
            connection.request('POST', '/solr/wikiru/update?wt=json', json_doc, headers)
            response = connection.getresponse()
            print(response.read().decode())
            #print("Entered")
            filecontent=''
            if isinstance(head, NavigableString):
                filecontent+=head
            if isinstance(head, Tag):
                filecontent+=head.get_text()
        head = head.nextSibling

    if subheading is None:
        subheading = "Introduction"
    commonkeywords =  set(javakeywords) & set(filecontent.split(' '))
    doc = {'add': {'doc': {'heading': heading, 'subheading': subheading, 'url' : url, 'content' : filecontent , 'keywords' : ' '.join(commonkeywords) }, 'boost': 1, 'overwrite': False, 'commitWithin': 1000}}
    json_doc = json.dumps(doc)
    connection.request('POST', '/solr/wikiru/update?wt=json', json_doc, headers)
    response = connection.getresponse()
    print(response.read().decode())
    #print("Entered")

    