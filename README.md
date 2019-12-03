# HistoCrop

Cut ROI or TMA spots from mrxs-images!

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What you need to install to get HistoCrop up and running:

* Matlab
* [MATLAB Engine API for Python](https://www.mathworks.com/help/matlab/matlab_external/get-started-with-matlab-engine-for-python.html)
  - Can be installed with the following commands at the matlab command prompt
  ```
  cd (fullfile(matlabroot,'extern','engines','python'))
  system('python setup.py install')
  ```
* Python3
  - openslide,os,sys,tkinter,texttable,cfonts,subprocess,csv,numpy,math,shutil,time

### Using the program

A step by step series of examples to show how to cut TMA spots out of multiple files.

Open terminal in the cropTMA folder and run `CropCode.py`.

```
cd /Users/jpohjone/Desktop/HistoCrop
python3 ./CropCode.py
```
```
██╗  ██╗ ██╗ ███████╗ ████████╗  ██████╗   ██████╗ ██████╗   ██████╗  ██████╗  
██║  ██║ ██║ ██╔════╝ ╚══██╔══╝ ██╔═══██╗ ██╔════╝ ██╔══██╗ ██╔═══██╗ ██╔══██╗
███████║ ██║ ███████╗    ██║    ██║   ██║ ██║      ██████╔╝ ██║   ██║ ██████╔╝
██╔══██║ ██║ ╚════██║    ██║    ██║   ██║ ██║      ██╔══██╗ ██║   ██║ ██╔═══╝  
██║  ██║ ██║ ███████║    ██║    ╚██████╔╝ ╚██████╗ ██║  ██║ ╚██████╔╝ ██║      
╚═╝  ╚═╝ ╚═╝ ╚══════╝    ╚═╝     ╚═════╝   ╚═════╝ ╚═╝  ╚═╝  ╚═════╝  ╚═╝      


Press R in case you want to crop a ROI from a WSIs
Press S in case you want to crop the Spots present in the TMAs
Press H in case you want to read the instructions:
```

Selecting `H` gives the help page, __which Valeria needs to update__.

Selecting `R` allows you to select a ROI from a whole slide image (WSI) and then cut it in sub-images. This can be useful
| in case it is necessary to select only a portion of the WSI. The following cut is implemented in     |
| order to work with the image that problably is in the order of ~GB.

```

| ROI: The ROI option allows to select a specif area and then cut it in sub-images. This can be useful |
| in case it is necessary to select only a portion of the WSI. The following cut is implemented in     |
| order to work with the image that problably is in the order of ~GB.                                  |
|                                                                                                      |
| The program will ask you:                                                                            |
|  - Input directory                                                                                   |
|  - Output directory                                                                                  |
|  - Dimesion of the square used for cut the ROI                                                       |
|                                                                                                      |
| A GUI is used to select the ROI.                                                                     |
|                                                                                                      |
| Suggestion: check the size in pixel of the WSI and then choose the dimension of the square according |
| to it.It is also better select the ROI considering the total width and white contours over and under |
| of the WSI.                                                                                          |
+------------------------------------------------------------------------------------------------------+
| Spot: The Spot option allows to reconize the spots in a TMA and cut them in order to obtain sigle    |
| image of spot per TMAs. If a document with the ID patients is attached it is possible to save each   |
| spot with the proper ID and in the corresponding folder per patient. if this is not the casey, the   |
| code will name the spots with a number from the bottom left to the upper right.                      |
| The program will ask you:                                                                            |
|                                                                                                      |
|  - Input directory                                                                                   |
|  - Output directory                                                                                  |
|  - Number of row in the TMA (remember to choose the maximum value considering all the TMAs)          |
|  - Number of column in the TMA (remember to choose the maximum value considering all the TMAs)       |
|                                                                                                      |
| A GUI is used to check if the program have found all the spots and, in case, allows to add or remove |
| incorrect elements.                                                                                  |
|                                                                                                      |
| Suggestion: Considering the IDpatient file, take a look to the example given with this code and      |
| rememeber to delete from the file those spots that you will remove in the GUI!                       |
+------------------------------------------------------------------------------------------------------+
```


```
  Function: Crops TMA spots out of mrxs-image

  Usage: $SELF -i [folder_of_mrxs_files] -r [max_rows] -c [max_cols]
               -m [matlab_location]
  Required inputs:

  -i    Folder of MRXS images
  -r    Maximum number of rows in TMA matrix
  -c    Maximum number of columns in TMA matrix
  -m    Location of matlab (MAC: /Applications/MATLAB_R2019a.app/bin/matlab, UNIX: use whereis)
```

3. Look at your slides and see what is the maximum number of rows and columns

4. Run cropTMA

```
./cropTMA -i ../TurkuTMA -r 8 -c 8 -m /Applications/MATLAB_R2019a.app/bin/matlab
```


6. Wait for the spots to be saved!

## Explanation of the workflow

A more detailed explanation of the workflow can be aquired by reading trough the code and comments (do'h).

**Generate thumbnails from the mrxs-files (python)**
  1. Create folder for output files (eg. TurkuTMA_images).
  2. Save label, macro and thumbnail images of the mrxs file.
  3. Find out mrxs-image dimensions using openslide and divide image into matrix of small images.
  4. Save small images with coordinates in the name.


**Determine spot locations using the thumbnail image (matlab)**
  1. Load the thumbnail images generated with mrxs_convert.
  2. Detect spot matrix coordinates from thumbnail image and crop the thumbnail image.
  3. For each thumbnail image detect spot coordinates.
    1. Create mask of spots and extract boundingBoxes.
    2. Rotate boundingBox centroids so that the coordinates can be used to determine column and row for each spot.
    3. Use hierarchical clustering to cluster x and y coordinates and then give each spot an id from the bottom-right to upper left corner.
    4. Create a summaryImage by drawign boundingBoxes and ids to the thumbnail image.


**Allow modification of the boundingBoxes (matlab)**
  1. Show summary image to the user.
  2. Ask user to redraw any boundingBox. Click image to continue.
  3. ASk user to remove any boundingBox. Click image to continue.
  4. Repeat until all summaryImages have been shown.


**Cut out each TMA spot (matlab)**
  1. Replace/remove any user defined boundingBoxes.
  2. Create folder for all the spots (eg. TurkuTMA_spots)
  3. Create a new summaryImg and save to output folder.
  4. Reconstruct spot matrix area of the TMA image using the coordinates detected earlier.
  5. Create folder for the TMA being processed (eg. TurkuTMA_spots/TMA_1)
  6. Crop out each spot using the boundingBox coordinates.



## Built With

  * [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
  * [Maven](https://maven.apache.org/) - Dependency Management
  * [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Authors

* **Valeria Ariotta**
* **Joona Pohjonen**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
