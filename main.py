#!/usr/bin/env python

############################
# fuzzylas
# by Matt, December 2012
# Looks up curve mnemonics
# Using data from spwla.org


############################
# Import libraries
import webapp2
#from google.appengine.ext import db
import json
import fuzzylas
import csv
import jinja2
import os
#import time

def datetimeformat(value, format='%H:%M on %d.%m.%Y'):
    return value.strftime(format)

############################
# Set up the template stuff
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

jinja_env.filters['datetimeformat'] = datetimeformat

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


############################
# Read the datafile and build a data store
# Use a dictionary since we don't need a dynamic store
# I'm pretty sure it only does this once, on deployment

with open('data/curves.csv') as dbfile:
    reader = csv.reader(dbfile)
    curves = {}
    for row in reader:
        record = {"company": row[0],
                  "type": row[1],
                  "method": row[2],
                  "mnemonic": row[3],   # redundant but useful in result lists
                  "model": row[4],
                  "units": row[5],
                  "unittype": row[6],
                  "description": row[7],
#                  "remark": row[8]      # handle later - some fields are blank
                  }
        curves.setdefault(str(row[3]), []).append(record)
 

############################
# Handlers

class MainHandler(Handler):
    def get(self):
        self.render("index.html")
        
    def post(self):
        input = self.request.get('mnemonic').upper()
        guess = fuzzylas.guess(curves,input,'simple',3)
        self.render("index.html", input=input, result=guess[0], order=sorted(guess[1],key=guess[1].get))

class AboutHandler(Handler):
    def get(self):
        self.render("about.html")
        
class ApiHandler(Handler):
    def get(self):
		
		guess = None
		
		if self.request.arguments() == []:
			self.render("help.html")
			
		else:
			mnemonic = self.request.get('mnemonic')
			method  = self.request.get('method')
			format  = self.request.get('format')
			guesses = self.request.get('guesses')
				
			if mnemonic:
				mnemonic = mnemonic.upper()
			else:
				mnemonic=""
				
			if method:
				method = method.lower()
			else:
				method = "simple"
	
			if format:
				format = format.lower()
	
			if guesses:
				guesses = int(guesses)
			else:
				guesses = 1        
				
			guess = fuzzylas.guess(curves,mnemonic,method,guesses)
				
			if format == "json":
				self.response.headers['Content-Type'] = 'application/json'
				self.response.out.write(json.dumps(guess))
				
			elif format == "csv":
				dump = 'mnemonic,company,method,description,units\n'
				for g in sorted(guess[1],key=guess[1].get):
					for i in guess[0][g]:
						dump = dump + str(g) + ',' + str(i['company']) + ',' + str(i['method']) + ',' + str(i['description'])+ ',' + str(i['units']) + '\n'
				self.response.headers['Content-Type'] = 'text/plain'
				self.response.out.write(dump)
				
			else:
				self.response.out.write(guess)


##############################
# This is the app itself

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/lookup', ApiHandler),
    ('/about', AboutHandler)
], debug=True)
