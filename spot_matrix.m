%This function is used to find the spot matrix coordinates from mrxs
%thumbnail image
%
%INPUT:
%       -thumbnail: Thumbnail file path
%
%OUTPUT:
%       -mat_coord: Spot matrix coordinates [xmin xmax ymin ymax]
%
% Ariotta Valeria  & Pohjonen Joona
% June 2019

function [mat_coord] = spot_matrix(thumbnail, radius)

%Grayscale conversion
Igray=rgb2gray(thumbnail);

%Operantion to create a mask in which the spots are well visible
Igray = imadjust(Igray);
Ibw=~imbinarize(Igray);

%Remove small specs
Ibw = bwareaopen(Ibw,200);

%Detect the matrix
se = strel('disk',radius,0);
Ibw_mat = imdilate(Ibw,se);
Ibw_mat = bwareafilt(Ibw_mat,1);
%Caclulate bounding box
bb = regionprops(Ibw_mat,'BoundingBox');

%Bounding box to min and max values for x and y
xMin = ceil(bb.BoundingBox(1));
xMax = xMin + bb.BoundingBox(3) - 1;
yMin = ceil(bb.BoundingBox(2));
yMax = yMin + bb.BoundingBox(4) - 1;

%Save coordinates
mat_coord = [xMin xMax yMin yMax];
end


