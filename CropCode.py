#Crop code to crop both spots in TMA samples or ROI in WSI samples. The input images must be in MIRAX format.

import cfonts
from tkinter import filedialog
from tkinter import *
import os
import openslide
import matlab.engine
from Classes import Crop
import texttable as tt

#Function to choose the input and output folder
def in_out():

	#Window to select the input folder
	print('Please select the input directory')
	root = Tk()
	root.withdraw()
	input_dir = filedialog.askdirectory(parent=root)
	root.update()
	root.destroy()

	#Window to select the output folder
	print('Please create/select an empty output directory')
	stop = True
	while stop:
		root = Tk()
		root.withdraw()
		output_dir = filedialog.askdirectory(parent=root)
		root.update()
		root.destroy()
		if len(os.listdir(output_dir)) == 0:
			stop = False
		else:
			print('Please create/select an EMPTY output directory')

	#Check of the folders
	mrxs=0
	fold=0
	for sample in os.listdir(input_dir):
		if sample.endswith('.mrxs'):
			mrxs+=1
		elif os.path.isdir(input_dir + '/' + sample):
			fold+=1
	if mrxs!=fold: #The input folder must has MIRAX format files (.mrxs+.data)
		print('ERROR! There is a problem in the MIRAX files in the input folder.\nThe input folder should contains '
			  'files with the extension .mrxs and the same number of foders with the .dat files')
		quit()

	return input_dir,output_dir


if __name__ == '__main__':

	#Program title
	Title = cfonts.render('HistoCrop', colors=['bright_white', 'white'])
	print(Title)

	#Selection of the two possible funciton: ROI crop, Spot crop + Help instructions
	select_def=str(input('Press R in case you want to crop a ROI from a WSIs\nPress S in case you want to crop the '
							 'Spots present in the TMAs\nPress H in case you want to read the instructions: '
							 ).upper())

	#ROI crop selection
	if select_def=='R':
		print('ROI crop selected')
		(input_dir,output_dir)=in_out()
		#ROI class call
		Crop(input_dir, output_dir).ROI()

	#Spot crop selection
	elif select_def=='S':
		print('Spot crop selected')
		(input_dir,output_dir)=in_out()
		#Spot class call
		Crop(input_dir, output_dir).Spot()

	#Help selection
	elif select_def=='H':
		print('Help selected')
		table = tt.Texttable()
		table.header(["Instructions"])
		table.add_row(["The present code allows to manage MIRAX files of histological samples. Two possible solutions were implemented:\n\n 1) Select a specific region of interest(ROI) from the whole slide image (WSI) and then cut it in sub-images\n 2) Find the spots in a TMA sample and cut them in sigle images"])
		table.add_row(["Prerequisites:\n1) Matlab\n  - MATLAB Engine API for Python\n2) Python3 \n  - openslide,sys, os, time, csv, pandas, numpy, texttable"])
		table.add_row(["How to run:\n - Open the terminal in the code folder and write:\n\n\tPython CropCode.py\n\nThen follow simply answer to the question!"])
		table.add_row(["ROI: The ROI option allows to select a specif area and then cut it in sub-images. This can be useful in case it is necessary to select only a portion of the WSI. The following cut is implemented in order to work with the image that problably is in the order of ~GB.\n"\
		"\nThe program will ask you:\n - Input directory\n - Output directory\n - If you want only the files with the dimension of the ROI or if you want to cut it directly with this program\n - Dimesion of the square used for cut the ROI, in case your answer was 'y' (yes) to the previous question\n\nA GUI is used to select the ROI.\n\nSuggestion: check the size in pixel of the WSI and then choose the dimension of the square according to it."\
		"It is also better select the ROI considering the total width and white contours over and under of the WSI."])
		table.add_row(["Spot: The Spot option allows to reconize the spots in a TMA and cut them in order to obtain sigle image of spot per TMAs. If a document with the ID patients is attached it is possible to save each spot with the proper ID and in the corresponding folder per patient."\
		" if this is not the casey, the code will name the spots with a number from the bottom left to the upper right.\nThe program will ask you:\n\n - Input directory\n - Output directory\n - Number of row in the TMA (remember to choose the maximum value considering all the TMAs)\n - Number of column in the TMA (remember to choose the maximum value considering all the TMAs)\n - Dimension of the radius in case the detected matrix of the spots is not correct"\
		"\n\nA GUI is used to check if the program have found all the spots and, in case, allows to add or remove incorrect elements.\n\nSuggestion: Considering the IDpatient file, take a look to the example given with this code!"])
		table.set_cols_width([100])
		print(table.draw())
	#In case of unknown character
	else:
		print('ERROR!Command not reconized!')
		quit()
