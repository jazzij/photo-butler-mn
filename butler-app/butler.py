'''
Eventually this needs to be deployed to be useful
https://coderwall.com/p/pstm1w/deploying-a-flask-app-at-heroku


'''
import os
from flask import  Flask, request, render_template, flash, url_for, send_from_directory
from werkzeug.utils import secure_filename 
import facefinder  
from app import app


UPLOAD_FOLDER = './uploads/'
RESULTS_FOLDER = './results/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
	return render_template("index.html", filename="none")
	#return "Hellow world. Welcome to photo butler"

''' 
UPLOAD FILES 
'''
@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
	if request.method == 'GET':
		return render_template("upload.html")	
			
	if request.method == 'POST':
		if 'photo' not in request.files:
			print('File part absent')
			flash('No file selected')
			return redirect(request.url), 400
		
		file = request.files['photo']
		
		if file.filename =='':
			print ('blank filename')
			flash('No file selected')
			return redirect(request.url), 400
		
		print ("ok, got "+file.filename)

		if file and allowed_file(file.filename):
			#save file & send back the filename
			fn = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
			return render_template('index.html', filename=file.filename)

	return
	
''' DISPLAY UPLOADED PHOTO(S) '''
@app.route("/file/<filename>", methods=['GET'])
def get_uploaded_file(filename):
	target = os.path.join(os.getcwd(), "uploads/")
	print(target)

	if not os.path.isdir(target):
		print("... is not a directory")	
	
	fullPath = "".join([target, "filename"])
	print (fullPath)
	
	return send_from_directory("uploads", filename)


@app.route("/test")
def test():
	return "This is a test"