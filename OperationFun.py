import sys
import time
import os
import shutil
import openslide
import matlab.engine
import subprocess
import csv
import numpy as np
import math

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
    img.save(name,namecompress_level=0)

    if not transparency:
        subprocess.call("mogrify -background white -flatten \"%s\""%(name,), shell=True)

    return True


def cropper_ROI(MRXS,out_dir, width, answ, lvl=0,transparency=False, writeAll=False,verbose=False): #Code for cropping the ROI
    MRXS_folder = os.path.abspath(MRXS) #input folder
    out_dir = out_dir + "/_ROI/" #Output folder
    if not (os.path.exists(out_dir)):
            os.mkdir(out_dir)

    #Trasparency
    answ_transparency=input('Do you want enable the transparency option and save empty pixels as transparent (default: N)? [Y/N]: ').upper()
    while not answ_transparency in ['Y','N','']:
        answ_transparency=input('Do you want enable the transparency option and save empty pixels as transparent (default: N)? [Y/N]: ').upper()
    if answ_transparency=='Y':
        transparency=True
        print('Trasparency option enabled!')

    #WriteAll
    answ_write=str(input('Do you want enable the writeAll option and save images even if there is no content (default: N)? [Y/N]: ' ).upper())
    while not answ_write in ['Y','N','']:
        answ_write=str(input('Do you want enable the writeAll option and save images even if there is no content (default: N)? [Y/N]: ' ).upper())
    if answ_write=='Y':
        writeAll=True
        print('writeAll option enabled!')

    #Verbose
    answ_verbose=str(input('Do you want enable the verbose option, which will output way too much stuff (default: N)? [Y/N]: ').upper())
    while not answ_verbose in ['Y','N','']:
        answ_verbose=str(input('Do you want enable the verbose option, which will output way too much stuff (default: N)? [Y/N]: ').upper())
    if answ_verbose=='Y':
        verbose=True
        print('Verbose option enabled! You were warned...')

    #Load mrxs file names to be cut
    with open(os.getcwd()+'/mrxs_paths.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        MRXS_files = []
        for row in readCSV:
            MRXS_files.extend(row)

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


    # Tell which ROIs have been cut already
    for roi in done:
        print('\nROI',os.path.basename(roi), 'has already been cut.\n')

    if answ=='Y':
    	# Cut ROIs from images and save
    	ROI_numbers = np.unique(all_ROI[:,0]).astype(int)
    	for ROI in ROI_numbers:
    		# Read image with OpenSlide
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
    							sys.stdout.write("Converting image %d/%d\r" % (x+out_blocks[0]*y, out_blocks[0]*out_blocks[1]))
    					sys.stdout.flush()
    		print("The ROI of sample %s is saved in %smin %ss.S" % (os.path.splitext(os.path.basename(image))[0],int((time.time() - start_time)//60), int((time.time() - start_time)%60)))
    	os.remove(os.getcwd()+'/mrxs_paths.csv')
    	os.remove(os.getcwd()+'/all_ROI.csv')
    	os.remove(os.getcwd()+'/tmp_summaries.mat')
    	os.remove(os.getcwd()+'/List_Rect.mat')
    else:
    	print("Operation Completed!\nYou can find useful information in four file produced: mrxs_paths.csv, all_ROI.csv, tmp_summaries.mat, List_Rect.mat'. These can be used for the next phase of cut.")

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

    # Load spot names to be cut
    with open(os.getcwd()+'/spot_names.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        spot_names = []
        for row in readCSV:
            spot_names.extend(row)
        os.remove(os.getcwd()+'/spot_names.csv')
    spot_names = np.array([str(i) for i in spot_names])
    spot_names = spot_names.reshape(int(np.size(spot_names)/2),2)

    # Load spot names to be cut (from possible excel)
    if (os.path.exists(os.getcwd()+'/spot_names_name.csv')):
        with open(os.getcwd()+'/spot_names_name.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            spot_names_name = []
            for row in readCSV:
                spot_names_name.extend(row)
        os.remove(os.getcwd()+'/spot_names_name.csv')
        spot_names_name = np.array([str(i) for i in spot_names_name])
        spot_names_name = spot_names_name.reshape(int(np.size(spot_names_name)/2),2)

    # Open all_spots.csv and format
    with open(os.getcwd()+'/all_spots.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        all_spots = []
        for row in readCSV:
            all_spots.extend(row)
        os.remove(os.getcwd()+'/all_spots.csv')
    all_spots = np.array([float(i) for i in all_spots])
    all_spots = all_spots.reshape(int(np.size(all_spots)/6),6)

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

        # Get spots names
        tma_spot_names = list(spot_names[spot_names[:,0] == str(spot)][:,1])

        # Cut of each spots per TMA
        spot_number = 0
        for row in all_spots[all_spots[:,0] == spot,1:6]:
            row[1:5] = row[1:5]*scale
            row = row.astype(int)
            spot_image = reader.read_region((row[1],row[2]),0,(row[3],row[4]))

            spot_path = spot_folder + os.path.splitext(os.path.basename(image))[0]+'_spot_'+tma_spot_names[spot_number]+'.png'
            if not (os.path.exists(spot_path)):
                spot_image.save(spot_path)
            spot_number += 1

        print("All spots saved in %smin %ss." % (int((time.time() - start_time)//60), int((time.time() - start_time)%60)))

        if (os.path.exists(os.getcwd()+'/spot_names_name.csv')):
            # Save spots to folders based on patient ids
            tma_number = 1
            for tma in MRXS_files:
                mrxs_name = os.path.basename(os.path.splitext(tma)[0])
                tma_folder = out_dir + mrxs_name
                names = spot_names_name[spot_names_name[:,0].astype(int) == tma_number]
                names[:,0] = spot_names[spot_names[:,0].astype(int) == tma_number][:,1]
                names = names.tolist()
                for name in names:
                    patient_folder = tma_folder + '/' + name[1]
                    if not (os.path.exists(patient_folder)):
                        os.mkdir(patient_folder)
                    for file in os.listdir(tma_folder):
                        if mrxs_name in file:
                            if name[0] == file.split('spot_')[1].split('.')[0]:
                                shutil.move(tma_folder + '/' + file, patient_folder + '/' + file)
