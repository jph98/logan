#!/usr/bin/env python

# Simple log service agent to provide tailing (tailer) and grep (grin) services
# via a RESTful service (Flask)

import os.path
import yaml
import glob 
import tailer
import subprocess
import grin
import re
import uuid
from flask import Flask, url_for, render_template
from flask import request, session
from flask import make_response

app = Flask(__name__)

configurationfile = 'logagentconfig.yaml'
config = {}

#
# init config information on startup
#
def init():
	configfile = open(configurationfile, 'r')
	global config
	config = yaml.load(configfile)
	print config
	configfile.close()
	
#
# Index page
#
@app.route("/")
def index():
	return list()

def link(href, text):
	return '<a href="' + href + '">' + text + '</a>'
	
#
# List all files based on directory and extension
#
@app.route("/list/")
def list():

	# Only allow tail/grep on files in the directory
	validfiles = {}
	
	# Filter log files for dirs specified in the config
	for dir in config['directories']:		
		for ext in config['extensions']:
		
			# Glob for all files specified in the config
			paths = glob.glob(dir + "/*." + ext)
			for path in paths:

				# store dict of validfiles using the filename
				hindex = path.rfind('/')
				filename = path[hindex+1:]
				
				# Generate URLs
				if os.path.getsize(path) > 0:
					size = str(os.path.getsize(path))
					uniquefilename = filename + "_" +  str(uuid.uuid1())
					print "Added " + path + " " + uniquefilename
					validfiles[uniquefilename] = [path, size]
		
	session['grepnumlines'] = str(config['grepnumlines'])	
	session['searchbeforecontext'] = str(config['searchbeforecontext'])	
	session['searchaftercontext'] = str(config['searchaftercontext'])	
	session['validfiles'] = validfiles
	return render_template('list.html')


@app.route("/tail/<filename>/<numlines>/")
def tail(filename, numlines=200):
	return processfile(tailer.tail, filename, int(numlines))
 
@app.route("/head/<filename>/<numlines>/")
def head(filename, numlines=200):
	return processfile(tailer.head, filename, int(numlines))	

#
# Process a file using a given function and a set of arguments
#
def processfile(fn, filename, numlines):
	validfiles = session.get('validfiles')
	if filename in validfiles:
		logpath = validfiles[filename][0]
		logfile = open(logpath, 'r')
		
		# pass generic function name
		lines = fn(logfile, numlines)
		
		content = '<br>'.join(lines)
		return render_template('content.html', content=content)
	else:
		resp = make_response(render_template('content.html'), 200)
		session['content'] = 'Refusing to process file'
		return resp
   
#
# Grep through a file looking for a phrase
# TODO: Fix bad GET request
@app.route("/grep/", methods=['GET', 'POST'])
def grep(): 

	if request is None or request.form is None:
		return render_template('list.html',error='no search expression specified')
		
	# Validate the form inputs
	if request.form['expression'] is None or len(request.form['expression']) == 0:
		return render_template('list.html',error='no search expression specified')

	expression = request.form['expression']
	expression = expression.strip()
	
	grepbefore = request.form['grepbefore']
	grepafter = request.form['grepafter']
	validfiles = session.get('validfiles')

	print "Grep (before) " + str(grepbefore)
	print "Grep (after) " + str(grepafter)
	print "Expression (regex) " + expression
	print "Filelist " + str(validfiles)
	
	options = grin.Options()
	options['before_context'] = int(grepbefore)
	options['after_context'] = int(grepbefore)
	options['use_color'] = False
	options['show_filename'] = False
	options['show_match'] = True
	options['show_emacs'] = False
	options['show_line_numbers'] = True
	
	print "Grin Options: " + str(options)
	
	output = ""
	filepaths = []
	
	# TODO: Fix regular epxressions
	searchregexp = re.compile(expression)
	
	grindef = grin.GrepText(searchregexp, options)
	anchorcount = 1
	for file in validfiles:
		filepath = validfiles.get(file)[0]
		report = grindef.grep_a_file(filepath)
		if report:
		
			# Generate the anchor tag
			output += '<a name="filename' + str(anchorcount) + '"></a><h2>' + filepath + '</h2>'
				
			filepaths.append(filepath)
			reporttext = report.split("\n")
			for text in reporttext:
				if text:
					output += "line " + text + "<br>"
			anchorcount += 1;
	
	# Return error msg if no results found
	if not output:
		return render_template('list.html', error='No results found for search expression')
		
	# Decode the output
	encodedoutput = output.decode('utf-8')
	
	# Highlight the matches
	expression = expression.decode('utf-8')
	
	highlight = '<span class="highlightmatch">' + expression + '</span>'
	
	highlightedoutput = encodedoutput.replace(expression, highlight)
	
	return render_template('results.html', output=highlightedoutput,filepaths=filepaths,expression=expression)

#
# Main method
#
if __name__ == "__main__":
	init()
	
	# TODO: Remove before release
	app.debug = True
	app.secret_key = 'A0Zr97sfas8j/asdkj R~XHH!jkjaLWX/,?RT'
	app.run(host='0.0.0.0')
