
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


connection = http.client.HTTPConnection("ec2-34-214-75-67.us-west-2.compute.amazonaws.com",8983)
headers = {'Content-type': 'application/json'}
solr = pysolr.Solr('http://ec2-34-214-75-67.us-west-2.compute.amazonaws.com:8983/solr/wikiru/', timeout=10)
new_urls = deque(['https://en.wikibooks.org/wiki/Java_Programming/'])
java_base_url = '/wiki/Java_Programming'
processed_urls = set()
f = open("java.txt")
keywords = f.readlines()
f.close()
javakeywords = [line.strip() for line in keywords]

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
    result = soup.find("div", {"id": "mw-content-text"})
    
    for element in result(text=lambda text: isinstance(text, Comment)):
        element.extract()

    unwanted = result.find_all("table", {"class": "wikitable"})
    for a in unwanted:
        a.extract()

    unwanted = result.find_all("table", {"class": "noprint"})
    for a in unwanted:
        a.extract()

    unwanted = result.find_all("div", {"id": "mw-navigation"})
    for a in unwanted:
        a.extract()

    unwanted = result.find_all("div", {"id": "footer"})
    for a in unwanted:
        a.extract()

    try:
        heading = soup.find("h1", {"id": "firstHeading"})
        heading = heading.text
        heading = heading.replace("/"," ")
        heading = heading.replace(" "," ")
    except:
        heading = soup.find("h1")
        heading = heading.text
        heading = heading.replace("/"," ")
        heading = heading.replace(" "," ")
    filecontent = ''
    i = 0
    file = open("data/"+heading+".txt","a+")
    doc = '{ ' 
    for header in soup.find_all('h2'):
        nextNode = header
        filecontent=''
        introcontent=''
        if i==0:
            introTagHeader = nextNode.findAllPrevious("p")
            introcontent=''
            for introTag in introTagHeader:
                finalintroTag = introTag
                introTag = introTag.nextSibling
            
            while True:
                finalintroTag = finalintroTag.nextSibling
                if finalintroTag is None:
                    break
                if isinstance(finalintroTag, NavigableString):
                    introcontent+=finalintroTag
                if isinstance(finalintroTag, Tag):
                    if finalintroTag.name == "h2":
                        break
                    introcontent+=finalintroTag.get_text()
            commonkeywords =  set(javakeywords) & set(introcontent.split(' '))
            foo = {'add': {'doc': {'heading': heading, 'subheading': 'Introduction', 'url' : url, 'content' : introcontent, 'keywords' : ' '.join(commonkeywords) }, 'boost': 1, 'overwrite': False, 'commitWithin': 1000}}
            json_doc = json.dumps(foo)
            connection.request('POST', '/solr/wikiru/update?wt=json', json_doc, headers)
            response = connection.getresponse()
            print(response.read().decode())

            i = i +1
            file.write(introcontent)
            file.close()
            introcontent=''
            filecontent=''
        
        try:
            subheading = nextNode.contents[0].text
            subheading = subheading.replace("/"," ")
            subheading = subheading.replace(" "," ")
        except:
            subheading = str(i)
        subfile = open("data/"+subheading+".txt","a+")
        while True:
            nextNode = nextNode.nextSibling
            if nextNode is None:
                break
            if isinstance(nextNode, NavigableString):
                filecontent+=nextNode
            if isinstance(nextNode, Tag):
                if nextNode.name == "h2":
                    break
                filecontent+=nextNode.get_text()

        commonkeywords =  set(javakeywords) & set(filecontent.split(' '))
        foo  = {'add': {'doc': {'heading': heading, 'subheading': subheading, 'url' : url, 'content' : filecontent, 'keywords' : ' '.join(commonkeywords) }, 'boost': 2, 'overwrite': False, 'commitWithin': 1000}}
        json_doc = json.dumps(foo)
        connection.request('POST', '/solr/wikiru/update?wt=json', json_doc, headers)
        response = connection.getresponse()
        print(response.read().decode())

        
        i = i +1
        subfile.write(filecontent)
        subfile.close()
        filecontent=''

    doc += "'commit': {},'optimize': {'waitSearcher': false }} "
    
    for anchor in soup.find_all("a"):
        link = anchor.attrs["href"] if "href" in anchor.attrs else ''
        if link.startswith('/'):
            link = base_url + link
        elif not link.startswith('http'):
            link = path + link
        if not link in new_urls and not link in processed_urls and ( java_base_url in link ) and "https://en.wikibooks.org/wiki/Java_Programming/Collection_Classes" not in link:
            new_urls.append(link)