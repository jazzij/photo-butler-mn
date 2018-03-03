from PhotoProject import PhotoProject

classobject = PhotoProject()
#classobject.save_find_faces("./pictures/"+"q2f1.png")
#classobject.save_find_faces("./pictures/"+"q2f2.png")

#distance = classobject.compare_faces("0189.jpg","1189.jpg")
#distance2 = classobject.compare_faces("0q2f1.png","0q2f2.png")
#print distance2
#print ("Distance between the two Images: "+ str(distance))
classobject.save_find_faces_all()
classobject.compare_all_faces()
#classobject.cluster_faces()
