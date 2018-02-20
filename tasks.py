from celery import Celery

broker_url = 'amqp://myuser:mypassword@54.69.82.183:5672/myvhost'
backend_url = 'rpc://myuser:mypassword@54.69.82.183:5672/myvhost'
app = Celery('tasks', broker=broker_url, backend = backend_url)

import face_recognition
from PIL import Image
from os import listdir

@app.task
def factorial(x,y):
    mul = 1
    for x1 in range(x,y+1):
        mul*=x1
    return mul

@app.task
def save_find_faces(filename):
    image = face_recognition.load_image_file(filename)
    face_locations = face_recognition.face_locations(image)
    img = Image.open(filename)
    counter = 0
    filename = filename.split('/')[-1]

    for x in face_locations:
        img2 = img.crop((x[3],x[0],x[1],x[2]))
        img2.save('faces/'+str(counter)+filename)
        counter += 1