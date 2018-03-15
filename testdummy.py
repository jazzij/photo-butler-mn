import face_recognition
def save_find_faces(filename):
    image = face_recognition.load_image_file(filename)
    face_locations = face_recognition.face_locations(image)
    img = Image.open(filename)
    counter = 0
    filename = filename.split('/')[-1]

    for x in face_locations:
        img2 = img.crop((x[3],x[0],x[1],x[2]))
        img2.save('faces/'+str(counter)+filename)
        print send_file_s3('faces/'+str(counter)+filename,str(counter)+filename,'faces/')
        os.remove('faces/'+str(counter)+filename)
        counter += 1