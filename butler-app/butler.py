'''
Eventually this needs to be deployed to be useful
https://coderwall.com/p/pstm1w/deploying-a-flask-app-at-heroku


'''
import os
from flask import  Flask, request, render_template, flash, url_for, send_from_directory
from werkzeug.utils import secure_filename 
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
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
		return render_template('index.html', filename="butler.jpg")

	return
	
''' ENTER PATHS OF FOLDERS THAT CONTAIN PHOTOS TO BE PROCESSED '''	
@app.route("/watch_folder", methods=['GET', 'POST'])
def watch_folder():
	return "watching"
	
''' DISPLAY UPLOADED PHOTO(S) '''
@app.route("/file/<filename>", methods=['GET'])
def send_image(filename):
	'''target = os.path.join(os.getcwd(), "uploads/")
	print(target)

	if not os.path.isdir(target):
		print("... is not a directory")	
	
	fullPath = "".join([target, "filename"])
	print (fullPath)'''
	
	return send_from_directory("uploads", filename)


@app.route("/gallery")
def gallery():
	photos = []
	for f in os.listdir(app.config['UPLOAD_FOLDER']):
		if allowed_file(f):
			photos.append(f)
	
	return render_template("gallery.html", image_names=photos)
	

@app.route("/facefun", methods=['GET', 'POST'])
def face_fun():	
	if request.method == 'GET':
		return render_template("gallery.html")
		
	if request.method == 'POST':
		return "sent info to /face_fun"
		#1. What operation is being requested (from button press)
		#2. What image will the operation be done on?	

@app.route("/highlight_faces/<filename>")
def highlight_faces(filename=None):
	if filename is None:
		return "highlight faces"
	else:
		return send_from_directory("uploads", filename)


@app.route("/custom_gallery")
def custom_gallery():
	return "custom gallery."	
