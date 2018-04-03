# import the necessary packages
import numpy as np
import argparse
import cv2
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image")
args = vars(ap.parse_args())
 
# load the image
image = cv2.imread("IMG_4382.jpg",1)
#resizes the image to fit on screen
r = 500.0 / image.shape[1]
dim = (500, int(image.shape[0] * r))
resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
image=resized

def selectPhotoWithColor(color):
        color=color.lower()
        # define the list of boundaries
        dict={"red":([17, 15, 100], [50, 56, 200]),
        "orange":([5, 50, 50],[15, 255, 255]),
        "yellow":([103, 86, 65], [145, 133, 128]),
        "green":([45, 100, 50], [75, 255, 255]),
        "blue":([25, 146, 190], [62, 174, 250]),
        "purple":([220,86,80],[255,160,255]),
        "pink":([170,100,0],[240,180,255]),
        "brown":([25,15,80],[34,45,200]),
        "black":([0,0,0],[179,50,45]),}
        boundries=dict[color]
        
        try:
                dict[color]
        except ValueError:
                print('Color not found')
        except:
                print('Error color not found')
                
        # create NumPy arrays from the boundaries
        low=boundries[0]
        up=boundries[1]
        lower = np.array(low, dtype = "uint8")
        upper = np.array(up, dtype = "uint8")

        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv2.inRange(image, lower, upper)
        output = cv2.bitwise_and(image, image, mask = mask)
        no_color_pix = cv2.countNonZero(mask)
        
        print('The number of '+color+' pixels is: ' + str(no_color_pix))
        print('The total number of pixels is: ' + str(image.size))

        # show the images for testing purposes 
        cv2.imshow("images", np.hstack([image, output]))
        cv2.waitKey(0)
selectPhotoWithColor("purple")
