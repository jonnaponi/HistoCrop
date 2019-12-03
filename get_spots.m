% Get spot_coordinates for cropper.py
%
%INPUT:
%       -mrxs_input: Folder of the converted mrxs files 
%       -mrxs_thumbnails: Outuput folder
%       -n_rows: Maximum number of rows in TMA
%       -n_cols: Maximum number of cols in TMA
%
% Ariotta Valeria  & Pohjonen Joona
% June 2019

function [r]=get_spots(mrxs_input,mrxs_thumbnails, n_rows, n_cols, radius, xlsx_path)
%Find thumbnails
tmp = dir(mrxs_thumbnails);
Folder = cell(1,length(tmp)-2);
for j=3:length(tmp)
    Folder{j-2} = cat(1,tmp(j).name);
end
thumbnails = Folder(contains(Folder,'.png'));
thumbnails = strcat(string(thumbnails));

%See which TMAs have been cut already
not_cut = [];

for i=1:length(thumbnails)
    %Folder for the spots
    mrxs_name = thumbnails{i};
    ind = strfind(mrxs_name,'.png');
    mrxs_name = mrxs_name(1:ind(end)-1);
    ind = strfind(mrxs_thumbnails,'_');
    output_path = [mrxs_thumbnails(1:ind(end)-1) '_spots' filesep mrxs_name];
    if ~exist(output_path, 'dir')
        not_cut = [not_cut i];
    end
end

if ~isempty(not_cut)
    %Initialize progress bar:
    upd = textprogressbar(length(thumbnails), 'barlength',30,'updatestep',1,...
        'startmsg','Loading thumbnails     ');
    
    %Preallocate cells to save data from thumbnails
    all_thumbnails = cell(length(thumbnails),1);
    all_mat_coord = cell(length(thumbnails),1);
    all_spots = cell(length(thumbnails),1);
    all_summaries = cell(length(thumbnails),1);
    all_angles = cell(length(thumbnails),1);
    all_spot_names_id = cell(length(thumbnails),1);
    all_spot_names_name = cell(length(thumbnails),1);
    
    for i=1:length(thumbnails)
        %Load thumbnail
        thumbnail = imread([mrxs_thumbnails filesep thumbnails{i}]);
        
        %Get spot matrix coordinates and crop thumbnail
        mat_coord = spot_matrix(thumbnail, str2double(radius));
        all_mat_coord{i} = mat_coord;
        thumbnail = thumbnail(mat_coord(3):mat_coord(4),mat_coord(1):mat_coord(2),:);
        
        %Get spot coordinates, summaryImg and the possible rotation angle
        [spots, summaryImg, angle] = spot_coord(thumbnail,n_rows,n_cols);
        
        %Save values
        all_mat_coord{i} = mat_coord;
        all_thumbnails{i} = thumbnail;
        all_spots{i} = spots;
        all_summaries{i} = summaryImg;
        all_angles{i} = angle;
        
        upd(i)
    end
    
    % Show GUI to user and fill remove_spots and new_spots
    save('tmp_summaries','all_summaries');
    Spot_Cut_Gui;
    waitfor(Spot_Cut_Gui)
    
    % Load variables saved from GUI
    load('List_Rect')
    
    % Initialize
    new_spots = cell(length(all_summaries),1);
    remove_spots = cell(length(all_summaries),1);
    
    % Change format for new spots
    for i=1:length(all_summaries)
        try
            %find the right coordinates for each image
            add_index = add_Img_num == i;
            new_spots{i} = {add_rect_data{add_index}};
        catch
            new_spots{i} = cell(1);
        end
        new_spots{i} = new_spots{i}';
    end
    
    %Cell to mat conversion
    for i=1:length(all_summaries)
        for ii=1:size(new_spots{i},1)
            tmp =  new_spots{i}{ii};
            new_spots{i}{ii,1} = tmp(1);
            new_spots{i}{ii,2} = tmp(2);
            new_spots{i}{ii,3} = tmp(3);
            new_spots{i}{ii,4} = tmp(4);
        end
    end
    
    % Change format for remove spots
    for i=1:length(all_summaries)
        try
            rem_index = rem_Img_num == i;
            remove_spots{i} = {rem_rect_data{rem_index}};
        catch
            remove_spots{i} = cell(1);
        end
        remove_spots{i} = remove_spots{i}';
    end
    
    %Cell to mat
    for i=1:length(all_summaries)
        for ii=1:size(remove_spots{i},1)
            tmp =  remove_spots{i}{ii};
            remove_spots{i}{ii,1} = tmp(1);
            remove_spots{i}{ii,2} = tmp(2);
            remove_spots{i}{ii,3} = tmp(3);
            remove_spots{i}{ii,4} = tmp(4);
        end
    end
    
    %Delete temporary *.mat files
    delete 'tmp_summaries.mat'
    delete 'List_Rect.mat'
    
    %Get new spots based on user input
    all_spots = get_new_spots(all_spots,remove_spots,new_spots);
    
    %Find the correct order
    all_spots = get_order(all_spots, all_summaries, all_angles,...
        n_rows, n_cols);
    
    ind = strfind(mrxs_thumbnails,'_');
    spots_folder = [mrxs_thumbnails(1:ind(end)-1) '_spots'];
    if ~exist(spots_folder)
        mkdir(spots_folder);
    end
    
    %preallocate a cell to collect all mrxs_names to be cut
    mrxs_paths = cell(length(all_spots),1);
    
    %Write summaries for each TMA
    for tma_i=1:length(all_spots)
        
        %Folder for the spots
        mrxs_name = thumbnails{tma_i};
        ind = strfind(mrxs_name,'.png');
        mrxs_name = mrxs_name(1:ind(end)-1);
        
        output_name = [spots_folder filesep mrxs_name];
        
        %Save the path of the original mrxs file
        mrxs_paths{tma_i} = [mrxs_input '/' mrxs_name '.mrxs'];
                
        %Create and save summary image
        summaryImg = all_thumbnails{tma_i};
        summaryImg = insertShape(summaryImg,'Rectangle',all_spots{tma_i}(:,2:5),...
            'Color','red','LineWidth', 3);
        
        %If two spots still have same number add an index
        spot_nums = all_spots{tma_i}(:,1);
        ind = 1;
        new_spot_nums = string([spot_nums(1);zeros(length(spot_nums)-1,1)]);
        stop_excel = 0;
        for i=2:length(spot_nums)
            if spot_nums(i) == spot_nums(i-1)
                stop_excel = 1;
                if ind == 1
                    new_spot_nums(i-1) = strcat(string(spot_nums(i-1)),'_',string(ind));
                    ind = ind +1;
                    new_spot_nums(i) = strcat(string(spot_nums(i)),'_',string(ind));
                else
                    ind = ind +1;
                    new_spot_nums(i) = strcat(string(spot_nums(i)),'_',string(ind));
                end
            else
                new_spot_nums(i) = string(spot_nums(i));
                ind = 1;
            end
        end
        
        all_spot_names{tma_i} = new_spot_nums;
        all_spot_names_id{tma_i} = new_spot_nums;
        all_spot_names_name{tma_i} = new_spot_nums;
        
        %Add text to summaryImg
        for i=1:length(all_spots{tma_i})
            summaryImg = insertText(summaryImg,[all_spots{tma_i}(i,2)+1,all_spots{tma_i}(i,3)+1],...
                sprintf(new_spot_nums(i)),'BoxOpacity',0,'FontSize',32);
        end
        %Save summary images
        imwrite(summaryImg,[output_name '_id.png'],'Quality','100','Mode','lossless');
        
        %See if there's an excel file with idkeys
        if ~isempty(dir([xlsx_path filesep mrxs_name '.*']))
            stop_loop = 0;
            if stop_excel == 1
                output = ['There were some errors in the detection of spots. See the generated summary image for ', mrxs_name,'\n']
                fprintf(output)
                stop_loop = 0
            end
            
            try
                numbers = readcell([xlsx_path filesep mrxs_name],'Sheet',2);
                numbers = cellfun(@(x) string(x), numbers(2:end,2:end));
                numbers = str2double(numbers)';
                numbers = rmmissing(numbers,1,'MinNumMissing',n_rows);
                numbers = rmmissing(numbers,2,'MinNumMissing',n_cols);
            catch
                fprintf('Excel file does not exist or sheet 2 with number information not present!\n')
                stop_loop = 1;
            end
            
            try
                names = readcell([xlsx_path filesep mrxs_name],'Sheet',3);
                names = cellfun(@(x) string(x), names(2:end,2:end));
                names = rmmissing(names,1,'MinNumMissing',n_rows);
                names = rmmissing(names,2,'MinNumMissing',n_cols);
                names = names';
                
                %Change names to correct form
                missing_names = ismissing(names(1:end));
                
                for i=1:length(names(1:end))
                    if  missing_names(i)
                        names(i) = "missing";  
                    else
                        ind = strfind(names(i),'_');
                    names(i) = names{i}(1:ind-1);
                    end
                end
                
            catch
                fprintf('Excel file does not exist or sheet 3 with the name information not present!\n')
                stop_loop = 1;
            end
            
           % if length(names(1:end)) ~= n_rows * n_cols
           %     fprintf('Excel file and given maximum row and column lengths do not match!')
           %     stop_loop = 1;
           % end

            if stop_loop == 0
                names = flipud([numbers(:) names(:)]);
                names = names(all_spots{tma_i}(:,1)',:);
                names(ismissing(names(:,1)),1) = "NA";
                
                %Create and save name summary image
                summaryImg = all_thumbnails{tma_i};
                summaryImg = insertShape(summaryImg,'Rectangle',all_spots{tma_i}(:,2:5),...
                    'Color','red','LineWidth', 3);
                for i=1:length(names)
                    summaryImg = insertText(summaryImg,[all_spots{tma_i}(i,2)+1,all_spots{tma_i}(i,3)+1],...
                        names(i,2),'BoxOpacity',0,'FontSize',16);
                end
                imwrite(summaryImg,[output_name '_spot_name.png'],'Quality','100','Mode','lossless');
                
                %Create and save id summary image
                summaryImg = all_thumbnails{tma_i};
                summaryImg = insertShape(summaryImg,'Rectangle',all_spots{tma_i}(:,2:5),...
                    'Color','red','LineWidth', 3);
                for i=1:length(names)
                    summaryImg = insertText(summaryImg,[all_spots{tma_i}(i,2)+1,all_spots{tma_i}(i,3)+1],...
                        string(names(i,1)),'BoxOpacity',0,'FontSize',32);
                end
                imwrite(summaryImg,[output_name '_spot_number.png'],'Quality','100','Mode','lossless');
                
                all_spot_names_id{tma_i} = names(:,1);
                all_spot_names_name{tma_i} = names(:,2);
            end
        end
    end
    
    
    % Save spots to all_spots.csv, names to mrxs_names.csv and spot names
    % to spot_names.csv
    
    spot_mat = zeros(1,6);
    spot_names = zeros(1,2);
    spot_names_id = zeros(1,2);
    spot_names_name = zeros(1,2);
    
    for i=1:length(all_spots)     
        all_spots{i}(:,2:3) = all_spots{i}(:,2:3) + repelem(all_mat_coord{i}([1 3]), length(all_spots{i}),1);
        spot_mat = [spot_mat;repmat(i,length(all_spots{i}),1) all_spots{i}];
        spot_names = [spot_names;repmat(i,length(all_spot_names{i}),1) all_spot_names{i}];
        spot_names_id = [spot_names_id;repmat(i,length(all_spot_names_id{i}),1) all_spot_names_id{i}];
        spot_names_name = [spot_names_name;repmat(i,length(all_spot_names_name{i}),1) all_spot_names_name{i}];
    end
    writematrix(spot_mat(2:end,:),'all_spots.csv')
    writecell(mrxs_paths,'mrxs_paths.csv')
    writematrix(spot_names(2:end,:),'spot_names.csv')
    if exist(xlsx_path)
        writematrix(spot_names_id(2:end,:),'spot_names_id.csv')
        writematrix(spot_names_name(2:end,:),'spot_names_name.csv')
    end
    
else
    fprintf('\nAll spots have been cut.\n')
end
r="DONE";
end


