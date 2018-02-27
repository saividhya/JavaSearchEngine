Pre-req
-------

Docker
Python
Java

Docker
---------
Install docker

SOLR Installation
------------------
docker run -d -p 8983:8983 solr solr-create -c wiki

SOLR can be accessed at localhost:8983
The wikibook and oracle TM tutorial have been crawled, indexed using SOLR and hosted in AWS which can be accessed at
http://ec2-34-214-75-67.us-west-2.compute.amazonaws.com:8983/solr/wikiru

Crawler
-------

Separate crawlers are written for java programming and Oracle TM tutorial.
The SOLR path is given as ec2 path mentioned above. If it has to be changed then the IP in which SOLR is setup should be given
python3 crawler.py
python3 oraclecrawler.py

Django API
-----------

In order to communicate with SOLR and retrieve result REST APIs are explosed using django application. This can be found in solr_api folder
cd solr_api
python manage.py runserver

Web Application
----------------

The web application can be run using following command

cd logging_app
gulp serve


