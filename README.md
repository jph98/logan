Logan Log Viewer
================

![Logan Screenshot](https://raw.githubusercontent.com/jph98/logan/master/logan.png)

Logan is a web based interface real-time log viewer/searcher.

Built upon:
* Python 2.6 
* Flask (Provides a simple web interface) - http://flask.pocoo.org/
* Pytailer (tail comamnd wrapper) - http://code.google.com/p/pytailer/ 
* Grin (grep command wrapper) - http://pypi.python.org/pypi/grin

Installation
------------

Install dependencies with:

    sudo pip install flask pyyaml tailer grin
    
Then run:

    ./logagent.py

Configuration
-------------

Look at logagentconfig.yaml:

Specifies the number of lines to display maximum:

    grepnumlines: 250
    
Specifies the number of lines before/after the match to display:

    searchbeforecontext: 2
    searchaftercontext: 2

Specifies the valid extensions for files found in 'directories':

    extensions:
     - log
     - out

To configure the directories to view/search within:

    directories:
     - /var/log
     - /Users/jonathan/temp

