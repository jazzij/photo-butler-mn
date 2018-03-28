from flask import Flask, render_template, request
from werkzeug import secure_filename
from modules import *
from difflib import SequenceMatcher
import httplib, urllib, base64, time, json
import sys
sys.path.append('../')
from PhotoProject import *
app = Flask(__name__)

@app.route('/')
def upload_file():
   return render_template('index.html')

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file1():
   if request.method == 'POST':
        f = request.files['file']
        f.save('Downloaded/'+secure_filename(f.filename))
        print 'File Recieved'
        return render_template('images.html',options=(eval_against_face(secure_filename(f.filename),'Downloaded/'+secure_filename(f.filename))))


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=81, debug = True)



