from PhotoProject import PhotoProject

classobject = PhotoProject()

classobject.save_find_faces("./pictures/"+"189.jpg")

distance = classobject.compare_faces("0189.jpg","1189.jpg")

print ("Distance between the two Images: "+ str(distance))