from PhotoProject import PhotoProject

classobject = PhotoProject()

classobject.save_find_faces("./pictures/"+"stat.jpg")

distance = classobject.compare_faces("0189.jpg","1189.jpg")
distance2 = classobject.compare_faces("0189.jpg","0hqdefault.jpg")
print distance2
print ("Distance between the two Images: "+ str(distance))