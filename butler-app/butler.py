'''
Eventually this needs to be deployed to be useful
https://coderwall.com/p/pstm1w/deploying-a-flask-app-at-heroku


'''
import os, time
from flask import  Flask, request, render_template, flash, url_for, send_from_directory
from werkzeug.utils import secure_filename 
from math import ceil
import facefinder  
from app import app



UPLOAD_FOLDER = './app/uploads/'
RESULTS_FOLDER = './app/results/'
SEARCH_FOLDERS = [] #user enters these
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 #5 MB upload limit


if __name__ == '__main__':
	app.run()

''' Check files '''
def allowed_file(filename):
	try:
		value = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
		return value
	except ValueError:
		return False
		
''' HOME / SPLASH PAGE
'''		
@app.route("/", methods=['GET'])
def index():
	print ('updated')
	return render_template("index.html", filename="none")
	#return "Hellow world. Welcome to photo butler"

''' 
UPLOAD FILES 
'''
@app.route("/upload", methods=['GET', 'POST'])
def upload():
			
	if request.method == 'GET':
		return render_template("upload.html")	

	#create upload folder if necessary
	if not os.path.isdir(app.config['UPLOAD_FOLDER']):
			os.mkdir(app.config['UPLOAD_FOLDER'])

	#handle false or empty file requests			
	if request.method == 'POST':
		if 'photo' not in request.files:
			print('File part absent')
			flash('No file selected')
			return redirect(request.url), 400
		
		file = request.files['photo'] #this object is a Werkzeug Multidict, with multiple values per key
		
		if file.filename =='':
			print ('blank filename')
			flash('No file selected')
			return redirect(request.url), 400
		
		print ("at least one file selected")
		
		#get all the files associated with form-key (in case multiple uploaded)
		allFiles = request.files.getlist('photo')
		print (allFiles)
		# save the files
		for file in allFiles:	
			if file and allowed_file(file.filename):
				#save file & send back the filename
				fn = secure_filename(file.filename)
				fullpath = os.path.join(app.config['UPLOAD_FOLDER'], fn)
				file.save(fullpath)
		return render_template('uploadconfirmation.html', upload=fn)

	return
	
''' ENTER PATHS OF FOLDERS THAT CONTAIN PHOTOS TO BE PROCESSED '''	
@app.route("/watch_folder", methods=['GET', 'POST'])
def watch_folder():
	return "watching"
	
'''  GALLERY of UPLOADED PHOTO(S) '''
'''Displays an list of uploaded photos. 
	Requires Gallery.html and UPLOAD folder
'''
@app.route("/gallery")
def gallery():
	photos = getUploadedPhotos()
	return render_template("gallery.html", image_names=photos, rows = len(photos))


''' EXECUTE PHoto OPTIONS. 
Requires Clickgallery.html for images with embedded links
Takes images from UPLOAD folder and saves to RESULTS folder, or API specified folder (see function for detail)
'''

# HIGHLIGHT FACES. Goto /highlight_faces to load the page. Click on any image. 
# The image will redirect here
@app.route("/highlight_faces/<filename>")
@app.route("/highlight_faces")
def highlight_faces(filename=None):
	if filename is None:
		photos = getUploadedPhotos()
		return render_template("clickgallery.html", image_names=photos, rows=len(photos), route="highlight_faces")
		
	else:
		#return send_from_directory("uploads", filename)
		facefinder.highlight_faces(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		while filename not in os.listdir("./results/"):
			pass
			
		return send_from_directory("results", filename)


#FIND A PERSON
#requires APP/DEMO_PICS folder for folder input
# input= filename, output = gallery page'''
@app.route("/find_person/<filename>")
@app.route("/find_person")
def find_person(filename=None):
	if filename is None:
		photos = getUploadedPhotos()
		return render_template("clickgallery.html", image_names=photos, rows=len(photos), route="find_person")	
	else:
		#return send_from_directory("uploads", filename)
		subjectPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		searchPath = os.path.join(os.getcwd(), 'app/demo_pics/') #hardcoded, but can select
		destPath = os.path.join(os.getcwd(), "./app/found_person/")
		facefinder.find_person(subjectPath=subjectPath, dirPath=searchPath, destPath=destPath, encoded=False)
		photos = getPhotos(destPath)
		return render_template("gallery.html", image_names=photos, rows = len(photos))
		

#SCRUB A PERSON
# requires APP/DEMO_PICS folder for folder input
# input file, output = gallery 	
@app.route("/scrub_person/<filename>")
@app.route("/scrub_person")
def scrub_person(filename=None):
	if filename is None:
		photos = getUploadedPhotos()
		return render_template("clickgallery.html", image_names=photos, rows=len(photos), route="scrub_person")
	else:
		#return send_from_directory("uploads", filename)
		subjectPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		searchPath = os.path.join(os.getcwd(), './app/demo_pics/') #hardcoded, but can select
		destPath = os.path.join(os.getcwd(), "./app/scrub_person/")
		facefinder.scrub(subjectPath, dirPath=searchPath, destPath=destPath, encoded=False)
		photos = getPhotos(destPath)
		return render_template("gallery.html", image_names=photos, rows=len(photos))
	


''' THESE ARE HELPER FUNCTIONS FOR THE ABOVE MAIN ROUTES'''
@app.route("/file/<filename>", methods=['GET'])
def send_image(filename, dir="uploads"):	
	return send_from_directory(dir, filename)


#Get photos from upload folder
def getUploadedPhotos():
	photos = []
	for f in os.listdir(app.config['UPLOAD_FOLDER']):
		if allowed_file(f):
			photos.append(f)
	return photos

#Get Photos from Any Folder, Results default	
def getPhotos(dir="./app/results/"):
	photos = []
	for f in os.listdir(dir):
		if allowed_file(f):
			photos.append(f)
	return photos

""" BOOLEAN FACES. NOT YET IMPLEMENTED
"""
@app.route("/boolean_faces", methods=['GET', 'POST'])
def boolean_faces():	
	if request.method == 'GET':
		return render_template("booleanfaces.html")
	
	#get info from request (type="submit" button)	
	if request.method == 'POST':
		#1. What operation is being requested (from button press)
		ops = ["AND", "OR", "NOT", "XOR"]
		for op in ops:
			if request.args.getlist(op) is not None: #request.args.getlist(op) should return a list of filenames
				names = request.args.getlist(op)
				#save to results folder
		#2. What images will the operation be done on?	
	return
	
