% Get spot_coordinates for cropper.py
%
%INPUT:
%       -mrxs_input: Folder of the converted mrxs files 
%       -mrxs_thumbnails: Outuput folder
%
% Ariotta Valeria  & Pohjonen Joona
% June 2019

function [r] = ROI_selection(mrxs_input,mrxs_thumbnails,answ)

%Find thumbnails
tmp = dir(mrxs_thumbnails);
Folder = cell(1,length(tmp)-2);
for j=3:length(tmp)
    Folder{j-2} = cat(1,tmp(j).name);
end
thumbnails = Folder(contains(Folder,'.png'));
thumbnails = strcat(string(thumbnails));

%See which ROIs have been cut already
not_cut = [];
ROI_mat=[];
for i=1:length(thumbnails)
    %Folder for the spots
    mrxs_name = thumbnails{i};
    ind = strfind(mrxs_name,'.png');
    mrxs_name = mrxs_name(1:ind(end)-1);
    ind = strfind(mrxs_thumbnails,'_');
    output_path = [mrxs_thumbnails(1:ind(end)-1) '_Summary' filesep mrxs_name '_Summary.png'];
    if ~exist(output_path)
        not_cut = [not_cut i];
    end
end

if ~isempty(not_cut)
    thumbnails = thumbnails(not_cut);
    
    %Initialize progress bar:
    upd = textprogressbar(length(thumbnails), 'barlength',30,'updatestep',1,...
        'startmsg','Loading thumbnails     ');
    
    %Preallocate cells to save data from thumbnails
    all_thumbnails = cell(length(thumbnails),1);
    for i=1:length(thumbnails)
        %Load thumbnail
        thumbnail = imread([mrxs_thumbnails filesep thumbnails{i}]);
        
        %Save values
        all_thumbnails{i} = thumbnail;
      
        upd(i)
    end
    
    % Show GUI to user and fill remove_spots and new_spots
    save('tmp_summaries','all_thumbnails');
    ROI_Cut_Gui;
    waitfor(ROI_Cut_Gui)
    
    % Load variables saved from GUI
    load('List_Rect')
    
    ind = strfind(mrxs_thumbnails,'_');
    spots_folder = [mrxs_thumbnails(1:ind(end)-1) '_Summary'];
    if ~exist(spots_folder)
        mkdir(spots_folder);
    end
    
    %Output in case of answ='N'
    Infocut_path=[mrxs_thumbnails(1:ind(end)-1) 'InfoCut/'];
    if answ=='N' & ~exist(Infocut_path)
        mkdir(Infocut_path)
    end
        
    %Write summaries for each TMA
    for tma_i=1:length(all_thumbnails)
        
        %Folder for the spots
        mrxs_name = thumbnails{tma_i};
        ind = strfind(mrxs_name,'.png');
        mrxs_name = mrxs_name(1:ind(end)-1);
        output_name = [spots_folder filesep mrxs_name];
        
        %Save the path of the original mrxs file
        mrxs_paths{tma_i} = [mrxs_input '/' mrxs_name '.mrxs'];
        
        
        %Create and save summary image
        summaryImg = all_thumbnails{tma_i};
        summaryImg = insertShape(summaryImg,'Rectangle',add_rect_data{tma_i}(:,1:4),...
            'Color','red','LineWidth', 3);

        %Save summary images
        imwrite(summaryImg,[output_name '_Summary.png'],'Quality','100','Mode','lossless');
           
        % Save the ROI to all_spots.csv and names to mrxs_names.csv
        ROI_mat = [ROI_mat; tma_i, add_rect_data{tma_i}];
    end
        if answ=='N'
            writematrix(ROI_mat,strcat(Infocut_path,'all_ROI.csv'));
            writecell(mrxs_paths,strcat(Infocut_path,'mrxs_paths.csv'));
        else
            writematrix(ROI_mat,'all_ROI.csv');
            writecell(mrxs_paths,'mrxs_paths.csv');
        end
else
    fprintf('\nAll ROIs have been cut.\n')
end
r="DONE";
end
