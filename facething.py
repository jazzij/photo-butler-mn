import face_recognition
from PIL import Image
from os import listdir


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
    
for x in listdir('./pictures/'):
    save_find_faces('pictures/'+x)
