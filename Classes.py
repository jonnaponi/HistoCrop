import sys
import time
import os
import matlab.engine
import OperationFun
import sys

class Crop():
	def __init__(self,input_dir, output_dir): #Initialization
		self.input_dir=input_dir
		self.output_dir=output_dir

	def ROI(self):
		input_dir=self.input_dir #inut folder
		output_dir=self.output_dir #output folder
		#Ask the dimension of the rectangle for extract the sub-images
		rect=raw_input('Dimension of the square, used for create the sub-images from the extracted ROI: ' )
		while 1: #Check if a inter nuber is chosen
			try:
				rect=int(rect)
				break
			except ValueError:
				rect=raw_input('ERROR! Not a number! Please enter the dimension of the square, used for create the sub-images from the extracted ROI: ' )

		OUTPUT_THUM_FOLDER=output_dir+"/_thumbnails" #Output folder
		os.mkdir(OUTPUT_THUM_FOLDER)

		print('Saving thumbnails...')
		for m in os.listdir(input_dir): #save the thumbnails images useful after in the code
			if m.endswith(".mrxs"):
				name=m[0:-5]
				OperationFun.Thumbnails(input_dir+"/"+m,OUTPUT_THUM_FOLDER+"/"+name) #Thumbnails function in OperationFun file
				time.sleep(1)

 		print("Detecting ROIs...") #GUI to manually select the ROI
 		Mat_Func=matlab.engine.start_matlab()
 		r=Mat_Func.ROI_selection(*(input_dir, OUTPUT_THUM_FOLDER),nargout=1)
		if r=="DONE":
			Mat_Func.quit()

		if not os.path.isfile('./all_ROI.csv'): #Images information are necessary!
			print('Error! The information for the ROI are not available!')
			quit()

		print("Saving ROI...") #Crop and save the previous selected ROI per image
		OperationFun.cropper_ROI(input_dir,output_dir,int(rect),0)
		
		
	def Spot(self):
		input_dir=self.input_dir #inut folder
		output_dir=self.output_dir #output folder

		row=raw_input('Number of spot per row, choose the maximum number possible: ' )
		col=raw_input('Number of spot per column, choose the maximum number possible: ' )

		while 1: #Check if a inter nuber is chosen
			try:
				row=int(row)
				break
			except ValueError:
				row=raw_input('ERROR! Not a number! Please enter the number of spot per row, choose the maximum number possible: ' )
		while 1: #Check if a inter nuber is chosen
			try:
				col=int(col)
				break
			except ValueError:
				col=raw_input('ERROR! Not a number! Please enter the number of spot per column, choose the maximum number possible: ' )

		OUTPUT_THUM_FOLDER=output_dir+"/_thumbnails" #Output folder for thumnails
		os.mkdir(OUTPUT_THUM_FOLDER)

		print('Saving thumbnails...')

		for m in os.listdir(input_dir): #save the thumbnails images useful after in the code
			if m.endswith(".mrxs"):
				name=m[0:-5]
				OperationFun.Thumbnails(input_dir+"/"+m,OUTPUT_THUM_FOLDER+"/"+name) #Thumbnails function in OperationFun file
				time.sleep(1)

 		print("Detecting ROIs...") #GUI to manually select each spot
 		Mat_Func=matlab.engine.start_matlab()
 		r=Mat_Func.get_spots(*(input_dir,OUTPUT_THUM_FOLDER, row, col),nargout=1)
		if r=="DONE":
			Mat_Func.quit()

		if not os.path.isfile('./all_spots.csv'): #Images information are necessary! 
			print('Error! The information for the Spot are not available!')
			quit()

		print("Saving Spots...") #Crop and save the previous selected spots per TMA
		OperationFun.cropper_Spots(input_dir,output_dir)

