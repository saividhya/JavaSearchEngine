# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from rest_framework.views import APIView

from django.http import JsonResponse
import pysolr
import json
import sys
from SolrClient import SolrClient
from rest_framework.response import Response
from rest_framework import status
from urllib2 import *
import simplejson 
import urllib
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import os

solr = SolrClient('http://localhost:8983/solr')


escapeRules = {'+': r'\+',
               '-': r'\-',
               '&': r'\&',
               '|': r'\|',
               '!': r'\!',
               '(': r'\(',
               ')': r'\)',
               '{': r'\{',
               '}': r'\}',
               '[': r'\[',
               ']': r'\]',
               '^': r'\^',
               '~': r'\~',
               '*': r'\*',
               '?': r'\?',
               ':': r'\:',
               '"': r'\"',
               ';': r'\;',
               '.': r'\.',
               '\'': r'\'',
               '"': r'\"'}

def escapedSeq(term):
    for char in term:
    	if char in escapeRules.keys():
            yield escapeRules[char]
        else:
            yield char

def escapeSolrArg(term):
    term = term.replace('\\', r'\\')   # escape \ first
    return "".join([nextStr for nextStr in escapedSeq(term)])


class SOLRView(APIView):
	def get(self,request,format=None):
		query=request.GET.get('query',None)
		query=urllib.unquote(query) 
		query=escapeSolrArg(query)
		print(query)

		module_dir = os.path.dirname(__file__)  # get current directory
		file_path = os.path.join(module_dir, 'java.txt')
		print(file_path)

		f = open(file_path)
		keywords = f.readlines()
		f.close()
		javakeywords = [line.strip() for line in keywords]
		print(javakeywords)
		stopWords = set(stopwords.words('english'))
		stopWords.remove("for")
		stopWords.remove("while")
		stopWords.add("was")
		stopWords.add("a")
		stopWords.add("an")
		stopWords.add("and")
		stopWords.add("are")
		stopWords.add("as")
		stopWords.add("at")
		stopWords.add("be")
		stopWords.add("but")
		stopWords.add("by")
		stopWords.add("for")
		stopWords.add("if")
		stopWords.add("in")
		stopWords.add("into")
		stopWords.add("is")
		stopWords.add("it")
		stopWords.add("no")
		stopWords.add("not")
		stopWords.add("of")
		stopWords.add("on")
		stopWords.add("or")
		stopWords.add("s")
		stopWords.add("such")
		stopWords.add("t")
		stopWords.add("that")
		stopWords.add("the")
		stopWords.add("their")
		stopWords.add("then")
		stopWords.add("there")
		stopWords.add("these")
		stopWords.add("they")
		stopWords.add("this")
		stopWords.add("to")
		stopWords.add("was")
		stopWords.add("will")
		stopWords.add("with")
		
		ps = PorterStemmer()
		words = query.split(" ")
		wordsFiltered = []

		commonkeywords = set(javakeywords) & set(query.split(' '))
		keywords='%20'.join(commonkeywords)
		
		for w in words:
			w=ps.stem(w)
			#if w not in stopwords:
			wordsFiltered.append(w)

		query = ' '.join(wordsFiltered)
		print(commonkeywords)
		query=urllib.quote(query)
		queryString = 'http://ec2-34-214-75-67.us-west-2.compute.amazonaws.com:8983/solr/wikiru/select?&wt=json&defType=edismax&fl=heading%20subheading%20url%20content%20keywords%20score&q=heading:'+'%20'.join(commonkeywords)+'%20subheading:'+'%20'.join(commonkeywords)+'%20keywords:'+'%20'.join(commonkeywords)+'%20content:'+query+'&qf=keywords^5%20heading^2%20subheading^2%20content^2'
		print(queryString)
		connection = urlopen(queryString)
		response = simplejson.load(connection)
		
		i=1
		result={}
		docresult=[]
		for document in response['response']['docs']:
			try:
				title = document['subheading']
			except:
				title = document['heading']
			if title=="Introduction":
				title=document['heading']
			doc = {'content':''.join(document['content']),'url':document['url'],'title':title,'score':document['score']}
			docresult.append(doc)
		  	i=i+1
		return JsonResponse(json.dumps(docresult),safe=False)