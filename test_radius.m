% Get radius for detecting the matrix
%
%INPUT:
%       -mrxs_thumbnails
%       -radius
%
% Ariotta Valeria  & Pohjonen Joona
% June 2019

function [r]=test_radius(thumbnail_path, radius)
    thumbnail = imread(thumbnail_path);
    Igray = rgb2gray(thumbnail);
    Igray = imadjust(Igray);
    Ibw = ~imbinarize(Igray);
    Ibw = bwareaopen(Ibw,200);
    Ibw_mat = imdilate(Ibw,strel('disk',double(radius),0));
    Ibw_mat = bwareafilt(Ibw_mat,1);
    imwrite(Ibw_mat,[thumbnail_path,'_matrix.png'],'Quality','20');
end