import sys
from cfonts import render, say
import Tkinter, tkFileDialog
import time
import os
import openslide
import matlab.engine
import subprocess
import csv
import pandas
import numpy as np
import math
import matplotlib.pyplot as plt

def Thumbnails(MRXS, fname):
	#Found the images and save the thumbnail file
	image=MRXS
	fname=fname+".png"
	reader = openslide.OpenSlide(image)

	level=reader.level_downsamples.index(64)
	thumbnail=reader.get_thumbnail(reader.level_dimensions[level])

	if not (os.path.exists(fname)): #A specific folder is created for the Thumbnail images
		thumbnail.save(fname)

def found_data(img):
	return any(  lo != 0 or hi != 0 for lo, hi in img.getextrema() )

def write_if_data(img,name,transparency,writeAll,verbose):
	#The Rois/Spots are saved
    if not writeAll:
        has_data=found_data(img)

        if not has_data:
        	return False
    if verbose:
        print("Found data, write image: "+name)
    #imgplot = plt.imshow(img)
    #plt.show()
    img.save(name,namecompress_level=0)

    if not transparency:
        subprocess.call("mogrify -background white -flatten \"%s\""%(name,), shell=True)
    
    return True


def cropper_ROI(MRXS,out_dir, width, lvl=0,transparency=False, writeAll=False,verbose=False): #Code for cropping the ROI
	MRXS_folder = os.path.abspath(MRXS) #input folder
	out_dir = out_dir + "/_ROI/" #Output folder
	if not (os.path.exists(out_dir)):
	        os.mkdir(out_dir)

	# Load mrxs file names to be cut
	with open(os.getcwd()+'/mrxs_paths.csv') as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    MRXS_files = []
	    for row in readCSV:
	        MRXS_files.extend(row)
	    os.remove(os.getcwd()+'/mrxs_paths.csv')
	#Consider with image analyses    
	MRXS_files_done = []
	for file in os.listdir(MRXS_folder):
	    if file.endswith(".mrxs"):
	        MRXS_files_done.append(os.path.join(MRXS_folder,file))
	        MRXS_files_done.sort()
	#Discard the images yet analysed
	done = []
	for peepoo in MRXS_files_done:
	    if not peepoo in MRXS_files:
	        done.append(peepoo)

	# Open all_ROI.csv and format
	with open(os.getcwd()+'/all_ROI.csv') as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    all_ROI = []
	    for row in readCSV:
	        all_ROI.extend(row)
	all_ROI = np.array([float(i) for i in all_ROI])
	all_ROI = all_ROI.reshape(int(np.size(all_ROI)/5),5)
	os.remove(os.getcwd()+'/all_ROI.csv')

	# Tell which ROIs have been cut already
	for roi in done:
	    print('\nROI',os.path.basename(roi), 'has already been cut.\n')


	# Cut ROIs from images and save
	ROI_numbers = np.unique(all_ROI[:,0]).astype(int)
	for ROI in ROI_numbers:
	    # Read image with openslide
	    image=MRXS_files[int(ROI-1)]
	    reader=openslide.OpenSlide(image)
	    print("\nProcessing image %s" % os.path.basename(image))
	    ROI_folder = out_dir + os.path.splitext(os.path.basename(image))[0] + "/"
	    if not (os.path.exists(ROI_folder)):
	        os.mkdir(ROI_folder)

	    start_time = time.time()

	    # Get downsampling factor and save it to scale
	    level=reader.level_downsamples.index(64)
	    dims=reader.dimensions
	    thumbnail_dims=reader.level_dimensions[level]
	    scale=dims[0]/thumbnail_dims[0]
	    
	    #Start to cut in sub images the selected ROI with the dimension chosen before.
	    for row in all_ROI[all_ROI[:,0] == ROI,1:5]:
	        row = row*scale
	        row = row.astype(int)
	        
	        ROI_path = ROI_folder + os.path.splitext(os.path.basename(image))[0]

	        px=width
	        scaledown=int(math.pow(2,lvl)) #In case of scaled image
	        dim_pad = str(max( [len(str(x)) for x in dims] ))
	    	out_dims=(float(row[2])/scaledown, float(row[3])/scaledown)
	    	out_blocks=( int(math.ceil( out_dims[0]/px )), int(math.ceil( out_dims[1]/px )) )
	    	print out_blocks
	    	print row
	        for y in range(out_blocks[1]):
	            for x in range(out_blocks[0]):
	                y_px = row[1]+y*px
	                x_px = row[0]+x*px
	                if verbose:
	                    sys.stdout.write("%d/%d\n" % (x+out_blocks[0]*y, out_blocks[0]*out_blocks[1] ))
	                #Each sub-image will have a name related to the chosen coordinates
	                wrote=write_if_data(reader.read_region((row[0]+scaledown*x*px,row[1]+scaledown*y*px),lvl,(px,px)),os.path.join(out_dir,("%s_-_y%0"+dim_pad+"d_x%0"+dim_pad+"d.png") % (ROI_path,y_px,x_px)),transparency,writeAll,verbose)
	                if not verbose:
	                    if wrote:
	                        sys.stdout.write("o")
	                    else:
	                        sys.stdout.write(".")
	                sys.stdout.flush()
	            sys.stdout.write("\n") 

	    print("The ROI of sample %s is saved in %smin %ss." % (os.path.splitext(os.path.basename(image))[0],int((time.time() - start_time)//60), int((time.time() - start_time)%60)))



def cropper_Spots(MRXS,out_dir): #Code for cropping the Spots
	# Get the folder of mrxs-images
	MRXS_folder = os.path.abspath(MRXS) #input folder
	out_dir = out_dir + "/_spots/" #output folder
	if not (os.path.exists(out_dir)):
	        os.mkdir(out_dir)
	# Load mrxs file names to be cut
	with open(os.getcwd()+'/mrxs_paths.csv') as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    MRXS_files = []
	    for row in readCSV:
	        MRXS_files.extend(row)
	    os.remove(os.getcwd()+'/mrxs_paths.csv')

	# Open all_spots.csv and format    
	with open(os.getcwd()+'/all_spots.csv') as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    all_spots = []
	    for row in readCSV:
	        all_spots.extend(row)
	all_spots = np.array([float(i) for i in all_spots])
	all_spots = all_spots.reshape(int(np.size(all_spots)/6),6)
	os.remove(os.getcwd()+'/all_spots.csv')

	# Cut spots from images and save
	spot_numbers = np.unique(all_spots[:,0]).astype(int)
	for spot in spot_numbers:
	    # Read image with openslide
	    image=MRXS_files[int(spot-1)]
	    reader=openslide.OpenSlide(image)
	    print("\nProcessing image %s" % os.path.basename(image))
	    spot_folder = out_dir + os.path.splitext(os.path.basename(image))[0] + "/"
	    if not (os.path.exists(spot_folder)):
	        os.mkdir(spot_folder)

	    start_time = time.time()

	    # Get downsampling factor and save it to scale
	    level=reader.level_downsamples.index(64)
	    dims=reader.dimensions
	    thumbnail_dims=reader.level_dimensions[level]
	    scale=dims[0]/thumbnail_dims[0]

	    idkeys_path = os.getcwd()+'/'+os.path.splitext(os.path.basename(image))[0]+'_idkeys.csv'
	    if os.path.exists(idkeys_path): #Considering if the id samples document is available
	        with open(idkeys_path) as csvfile: #If yes, then the correct number and name will be given to the spots
	            readCSV = csv.reader(csvfile, delimiter=',')
	            idkeys = []
	            for row in readCSV:
	                idkeys.extend(row)
	        os.remove(idkeys_path)
	        if len(idkeys)==all_spots[all_spots[:,0] == spot,1:6].shape[0]:
	            patient_wise = 1
	            i = 0
	        else:
	            patient_wise = 0
	    else:
	        patient_wise = 0
	    #Cut of each spots per TMA    
	    for row in all_spots[all_spots[:,0] == spot,1:6]:
	        row[1:5] = row[1:5]*scale
	        row = row.astype(int)
	        spot_image = reader.read_region((row[1],row[2]),0,(row[3],row[4]))

	        if patient_wise == 1: #Spot name with ID samples and saved in the folder specific for that patient
	            spot_path = spot_folder + idkeys[i] + '/'
	            if not (os.path.exists(spot_path)):
	                os.mkdir(spot_path) #Specific patient folder 
	            spot_name = spot_path + os.path.splitext(os.path.basename(image))[0]+'_spot_'+str(row[0])+'.png'
	            if not (os.path.exists(spot_name)):
	                spot_image.save(spot_name)
	            i += 1
	        else: #In the contrary case, the spot will numerate sequencially from bottom right to top left 
	            spot_path = spot_folder + os.path.splitext(os.path.basename(image))[0]+'_spot_'+str(row[0])+'.png'
	            if not (os.path.exists(spot_path)):
	                spot_image.save(spot_path)

	    print("All spots saved in %smin %ss." % (int((time.time() - start_time)//60), int((time.time() - start_time)%60)))
