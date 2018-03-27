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

@app.route('/demo')
def upload_file4():
   return render_template('hwr.html')

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file1():
   if request.method == 'POST':
        f = request.files['file']
        f.save('Downloaded/'+secure_filename(f.filename))
        print 'File Recieved'
        return str(eval_against_face(secure_filename(f.filename),'Downloaded/'+secure_filename(f.filename)))
#        return render_template('index.html')
        #return render_template('uploaded.html',x=k1, score=str(score)+str('/')+str(c+1))


@app.route('/hwr', methods = ['GET', 'POST'])
def upload_file2():
   if request.method == 'POST':
        f = request.files['file']
        f.save('Downloaded/'+secure_filename(f.filename))
        print 'File Recieved'
        domain = push_to_imgur('Downloaded/'+f.filename)
        print domain
        k = Handwriting_To_Text(domain)
        
        return '<h1>'+str(k)+'</h1>'


@app.route('/similarity/<text1>/<text2>', methods = ['GET', 'POST'])
def sim(text1,text2):
        k = text1
        k = k.replace(' ','%20')
        u = text2
        u = u.replace(' ','%20')

        url = "https://api.dandelion.eu/datatxt/sim/v1/?text1="+str(k)+"&text2="+str(u)+"&token=b3e2988c6d3343e8a5bbeea89acae0aa"
        print url
        f = urllib.urlopen(url)
        myfile = f.read()
        d = json.loads(myfile)
        return '<h2>'+str(float(d['similarity'])*100)+'% Similarity </h2>'

@app.route('/compress/<text1>')
def comp(text1):
        import summarize
        ss = summarize.SimpleSummarizer()
        return '<h2>'+str(ss.summarize(text1, 5))+'</h2>'

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=81, debug = True)



