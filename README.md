# PhotoProject

The project code uses modular Object Orientated Based approach.
The list of available modules:


----------


 **- `save_find_faces(filename, accessor="")`**
Automatically saves any found face into a folder. Naming convention is \[x\]\[photoID\].jpg (ie 01138, 11138, 21138)

	 Example:
	 `classobject.save_find_faces('IMG_0129.JPG','./pictures/')`
 


----------


**- `save_find_faces_all()`**
	 Automatically saves all found face into a folder. Naming convention is \[x\]\[photoID\].jpg (ie 01138, 11138, 21138)
	 
	 Example:
	 `classobject.save_find_faces_all()`
	 


----------


 **- `compare_faces(face1,face2)`**
	 Compare distance between two faces to see if its the same person.
.45 is optimal threshold (per face rec library, referencing CMU OpenFace algorithm)
Below .45 means its the same person, and above means its not.
	 
	 Example:
	 `classobject.compare_faces(face1,face2)`
	 


----------


 **- `compare_all_faces()`**
	 Compare distance between two faces to see if its the same person.
.45 is optimal threshold (per face rec library, referencing CMU OpenFace algorithm)
Below .45 means its the same person, and above means its not. Generating a CSV File crossreferencing for all files in faces/nonclustered.
	 
	 Example:
	 `classobject.compare_all_faces()`
	 


----------


 **- `cluster_faces(self,threshold=0.45)`**
	 Cluster faces in faces/nonclustered basef on similarity
	 Example:
	 `classobject.cluster_faces(self,threshold=0.45)`