Bug found:
find_person() and scrub_person() are unreliable - print statements have been
added to both to demonstrate the problem. find_person() is being called
twice - once on the uploaded picture, and once on "gallery.css". And then
facefinder.find_person() doesn't know what to do with a .css file.

Welcome to the Photo Butler Demo!

What do you need to run this code?
1) Check Requirements.txt for python dependencies
2) Install your very own personal Flask server: flask.pocoo.org 
3) Set your environment variables:
	$ export FLASK_DEBUG=1
	$ export FLASK_APP=butler.py
	$ flask run

Setup: 
APP_ROOT is here!  
the Routes are in APP_ROOT/butler.py  
the HTML is in APP_ROOT/templates/  
the javascript should go in APP_ROOT/static/  

Possible Routes:  
'/' : index, starter page  
'/upload' : upload one or multiple files  
'/gallery': see all uploaded files displayed  
'/highlight_faces' : highlight the face of your loved one in a group photo  
'/find_me': given a selfie, find all the photos of you in your collection  
