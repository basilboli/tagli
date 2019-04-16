#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Tagli tools
    ~~~~~~~~
    scripts to manage tags 

    :copyright: (c) 2012 by basilboli
    prohibited by real patsan's law.
"""
import os
import json
import argparse
import requests
import tagli
import string
import random
from tagli import app, mongo
import cairosvg
import subprocess
from Mailer import Mailer
import sh
from sh import ErrorReturnCode
import re

def send_welcome():
    return requests.post(
        "https://api.mailgun.net/v2/samples.mailgun.org/messages",
        auth=("api", "key-3ax6xnjp29jd6fds4gc373sgvjxteol0"),
        data={"from": "Tagli Team <welcome@sandbox129.mailgun.org",
              "to": ["basilboli@gmail.com"],
              "subject": "Welcome to the club.",
              "text": "Testing some Mailgun awesomness!"})    
	
def generate_codes(n, locale):
	print ("Generate %s new tags ..." %n)
	try:
		sh.mkdir("output")
	except ErrorReturnCode:
	    print("folder already exists")
	for i in range(n):
		while True:
			characters = re.sub('[0Oo5]', '', string.ascii_letters+string.digits)
			code_hash ='x'+''.join(random.choice(characters) for i in range(3)) 
			print ("Trying code: ",code_hash)
			with app.app_context():
				code = mongo.db.codes.find_one({"code_hash": code_hash})
			if code is None:			
				print ("Ok.")
				with app.app_context():
					mongo.db.codes.insert({"code_hash": code_hash})			
				generate_image(code_hash, locale)	
				break				
			else:
				"Trying again ..."
def generate_image(hash, locale):
	print ("Generating new image for ", hash) 
	template = "templates/tagli-{0}.svg".format(locale)	
	write_from = "output/svg/tagli-{0}-{1}.svg".format(locale,hash)
	write_to = "output/png/tagli-{0}-{1}.png".format(locale,hash)
	replaceTagCode(hash, template, write_from)	
	with open(write_from, 'rb') as file_object:
		cairosvg.svg2png(file_obj=file_object, write_to=write_to)

def main():
	parser = argparse.ArgumentParser(description='Manage this Tagli application.')
	parser.add_argument('command', help='Command')	
	parser.add_argument('number',  help='Number of tags', type=int)	
	parser.add_argument('locale',  help='Locale : en|fr')	
	args = parser.parse_args()

	if args.command == 'new':
		generate_codes(args.number, args.locale)
	else:
		print ("Error : Not supported command ...")	

def read_file(filename):
    """Shortcut to return the whole content of a file as a byte string."""
    with open(filename, 'rb') as file_object:
        return file_object.read()	

def replaceTagCode(hash, source, destination):
	""" Replaces existing template value with tag code """
	cmd= ["sed","s/XXXX/%s/g" % hash, source]
	subprocess.call(cmd, stdout=open(destination, 'w'))

if __name__ == '__main__':
	# replaceTagCode("kcff", "tags/tagli.svg", "tags/tagli-kcff.svg")	
	# send_welcome()
	# mail = Mailer()
	# mail.welcome('basilboli@gmail.com')
	main()



