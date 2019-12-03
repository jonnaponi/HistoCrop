import time
import os
import matlab.engine
import OperationFun
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


class Crop():
	def __init__(self,input_dir, output_dir): #Initialization
		self.input_dir=input_dir
		self.output_dir=output_dir

	def ROI(self):
		input_dir=self.input_dir #inut folder
		output_dir=self.output_dir #output folder
		#Ask if the user what to cut the WSI with the same program or not. Sometimes the number of WSI is big so it would be necessary used Anduril or another program
		#parallelize the cut process.
		answ=str(input('Do you want cut the WSI directly with this code?[Y,N]: ' ).upper())

		if answ=='Y':
			#Ask the dimension of the rectangle for extract the sub-images
			rect=input('Dimension of the square, used for create the sub-images from the extracted ROI: ' )

			while 1: #Check if a inter nuber is chosen
				try:
					rect=int(rect)
					break
				except ValueError:
					rect=input('ERROR! Not a number! Please enter the dimension of the square, used for create the sub-images from the extracted ROI: ' )
		else:
			rect=0

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
		OperationFun.cropper_ROI(input_dir,output_dir,int(rect),answ,0)

	def Spot(self):
		input_dir=self.input_dir #inut folder
		output_dir=self.output_dir #output folder

		row=str(input('Number of spot per row, choose the maximum number possible: ' ))
		col=str(input('Number of spot per column, choose the maximum number possible: ' ))

		while 1: #Check if a inter nuber is chosen
			try:
				row=int(row)
				break
			except ValueError:
				row=input('ERROR! Not a number! Please enter the number of spot per row, choose the maximum number possible: ' )
		while 1: #Check if a inter nuber is chosen
			try:
				col=int(col)
				break
			except ValueError:
				col=input('ERROR! Not a number! Please enter the number of spot per column, choose the maximum number possible: ' )

		excel = input('Do you have an excel file with spot information? [Y/N] ')
		while not excel in ['Y','N']:
			correct = str(input('Do you have an excel file with spot information? [Y/N] '))
		if excel == 'Y':
			print('Please select the excel directory')
			root = Tk()
			root.withdraw()
			excel_dir = filedialog.askdirectory(parent=root)
			root.update()
			root.destroy()
		if excel == 'N':
			excel_dir = 'none'

		OUTPUT_THUM_FOLDER=output_dir+"/_thumbnails" #Output folder for thumnails
		os.mkdir(OUTPUT_THUM_FOLDER)

		print('Saving thumbnails...')
		for m in os.listdir(input_dir): #save the thumbnails images useful after in the code
			if m.endswith(".mrxs"):
				name=m[0:-5]
				OperationFun.Thumbnails(input_dir+"/"+m,OUTPUT_THUM_FOLDER+"/"+name) #Thumbnails function in OperationFun file

		print('Checking TMA matrix...')

		correct = 'N'
		radius=100
		thumbnail =  OUTPUT_THUM_FOLDER + '/'+ os.listdir(OUTPUT_THUM_FOLDER)[0]
		Mat_Func = matlab.engine.start_matlab()

		while correct == 'N':
			Mat_Func.test_radius(*(thumbnail, radius), nargout=0)

			img1 = mpimg.imread(thumbnail)
			img2 = mpimg.imread(thumbnail + '_matrix.png')

			fig = plt.figure(figsize=(6,6))

			ax1 = fig.add_subplot(1,2,1)
			ax1.imshow(img1)
			ax1.axis('off')
			ax1.set_title('Thumbnail')
			ax2 = fig.add_subplot(1,2,2)
			ax2.imshow(img2, cmap='binary')
			ax2.axis('off')
			ax2.set_title('Detected matrix')

			plt.show(block=False)
			correct = str(input('Was the matrix detected correctly? [Y/N] '))
			plt.close('all')
			while not correct in ['Y','N']:
				correct = str(input('Was the matrix detected correctly? [Y/N] '))
			if correct == 'N':
				print('Previous radius: ' + str(radius))
				radius = input('Give a new radius (integer): ')

				while not isinstance(radius, int):
					try:
						radius = int(radius)
					except:
						radius = input('Give new radius (integer): ')
		os.remove(thumbnail + '_matrix.png')

		print("Detecting Spots...") #GUI to manually select each spot
		Mat_Func=matlab.engine.start_matlab()
		r=Mat_Func.get_spots(*(input_dir,OUTPUT_THUM_FOLDER, row, col, str(radius)), excel_dir,nargout=1)
		if r=="DONE":
			Mat_Func.quit()

		if not os.path.isfile('./all_spots.csv'): #Image information is necessary!
			print('Error! The information for the spots is not available!')
			quit()

		print("Saving Spots...") #Crop and save the previous selected spots per TMA
		OperationFun.cropper_Spots(input_dir,output_dir)
