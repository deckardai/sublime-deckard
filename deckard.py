import sublime
import sublime_plugin


DdHost = "localhost:3325"

import sys
import os
import json
from time import time

try:
    if sys.version_info[0] >= 3:
        import http.client as httplib
    else:
        import httplib

    # Detect vim flavor
    DdEditor = "sublime"
    # Get a unique name
    #DdEditor += ":" + str(int(time()))

    DdOk = True
except Exception as e:
    # httplib can fail mysteriously in unusual environments, ex. git commit
    DdOk = False



class Deckard(sublime_plugin.EventListener):

	def post(self, eventName, event):
	    " Fire and forget an event "
	    conn = httplib.HTTPConnection(DdHost, timeout=1)
	    conn.request(
	        "POST", "/" + eventName,
	        body=json.dumps(event),
	        headers={
	            "Content-Type": "application/json",
	        },
	    )
	    conn.close()

	def on_modified_async(self, view):
	    try:
	        path = view.file_name()
	        if not path:
                    return
	        self.post("change", {
	            "fullPath": path,
	        })
	    except Exception as e:
	        # Normal if Deckard is not running
	        pass

	def on_selection_modified_async(self, view):
	    try:
	        path = view.file_name()
	        if not path:
	            return

	        sel = view.sel()[0]
	        if sel.a == sel.b:
	            return

	        lineno, charno = view.rowcol(sel.a)

	        event = {
	            "path": path,
	            "lineno": lineno,
	            "charno": charno,
	            "editor": DdEditor,
	        }
	        self.post("event", event)
	    except Exception as e:
	        # Normal if Deckard is not running
	        pass


# No async support for Sublime 2, remove the _async suffixes
for method in ["on_selection_modified", "on_modified"]:
	method_async = method + "_async"
	if not hasattr(sublime_plugin, method_async):
		setattr(Deckard, method, getattr(Deckard, method_async))
		delattr(Deckard, method_async)
