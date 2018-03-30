import httplib, urllib, base64, time, json, sys
sys.path.append('../')
from flask import Flask, render_template, request
from werkzeug import secure_filename
from modules import *
from PhotoProject import *

app = Flask(__name__)

@app.route('/')
def upload_file():
   return render_template('index.html',ipaddress=get_ip())

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file1():
   if request.method == 'POST':
        f = request.files['file']
        f.save('Downloaded/'+secure_filename(f.filename))
        print 'File Recieved',
        return render_template('testimages.html',options=(eval_against_face(secure_filename(f.filename),'Downloaded/'+secure_filename(f.filename))))


if __name__ == '__main__':
        #save_find_faces_all('../pictures/','../faces/meta/','../faces')
        app.run(host='0.0.0.0', port=80, debug = True)