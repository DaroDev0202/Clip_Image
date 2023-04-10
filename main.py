import cv2 as cv
import PySimpleGUI as sg
import os
import piexif

from datetime import datetime
from threading import Thread
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

from variable import *
from imageai.Detection import ObjectDetection
# Load Object Recognition Model

current_dir = os.path.dirname(os.path.abspath(__file__))
classes_file = os.path.join(current_dir, "coco_classes.txt")

recognizer = ObjectDetection()
recognizer.setModelTypeAsTinyYOLOv3()
recognizer.setModelPath(PATH_MODEL)
recognizer.loadModel()

detectedFrameList = []

def extract_video(window, filePath, savePath, saveFrames = []):
    # Get File Name to Save
    file_name = os.path.basename(filePath)
    file_name = file_name[:-4]
    
    # Parsing Metadatas
    parser = createParser(filePath)
    metadata = extractMetadata(parser)
    
    created_time = ""
    for line in metadata.exportPlaintext():
        if "creation date" in line.lower():
            video_created_time = line
            created_time = line.split(": ")[1]

    if created_time == "":
        created_time = datetime.now()
    else:
        created_time = datetime.strptime(created_time, '%Y-%m-%d %H:%M:%S')
        
    # Check video file is valid
    video = cv.VideoCapture(filePath)
    if not video.isOpened():
        return
    
    if len(saveFrames) == 0 :       # Save All Frames
        ret, frame = video.read()
        # Calculate total frame
        
        totalFrame = int(video.get(cv.CAP_PROP_FRAME_COUNT))
        currentFrame = 1
        while ret:
            ret, frame = video.read()
            progress = currentFrame * 100 / totalFrame
            if frame is None:
                update_progress(window[CIRCULAR_PROGRESS], progress)
                setState(window, 'Extracting(' + str(currentFrame) +'/' + str(totalFrame) +' images completed)')
                currentFrame = currentFrame + 1
                continue
            
            output_path = savePath + '/' + file_name + "_" + str(currentFrame).zfill(8) + "_" + created_time.strftime('%Y-%m-%d_%H-%M-%S' + '.jpg')
                
            cv.imwrite(output_path, frame, [cv.IMWRITE_PNG_COMPRESSION, 0])
            
            with Image.open(output_path) as image:
                exif_dict = piexif.load(output_path)
                # exif_dict['Exif'][piexif.ImageIFD.DateTime] = created_time.strftime('%Y-%m-%d %H:%M:%S')
                # '2023: 03: 15 05: 11: 51'
                exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = created_time.strftime('%Y: %m: %d %H: %M: %S')
                exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = created_time.strftime('%Y: %m: %d %H: %M: %S')
                exif_bytes = piexif.dump(exif_dict)
                image.save(output_path, 'tiff', exif= exif_bytes)
                
            # piexif.insert(exif_bytes, output_path)
            print(exif_dict)
            
            update_progress(window[CIRCULAR_PROGRESS], progress)
            setState(window, 'Extracting(' + str(currentFrame) +'/' + str(totalFrame) +' images completed)')
            currentFrame = currentFrame + 1
    else :
        print(saveFrames)
        total_frames = len(saveFrames)
        
        currentFrame = 1
        finish_frame_cnt = 1
        ret, frame = video.read()
        # Calculate total frame
        
        while ret:
            if str(currentFrame).zfill(8) not in saveFrames:
                currentFrame = currentFrame + 1
                continue
            
            progress = finish_frame_cnt * 100 / total_frames
            ret, frame = video.read()
            
            output_path = savePath + '/' + file_name + "_" + str(currentFrame).zfill(8) + "_" + created_time.strftime('%Y-%m-%d_%H-%M-%S' + '.jpg')
                
            cv.imwrite(output_path, frame, [cv.IMWRITE_PNG_COMPRESSION, 0])
            
            with Image.open(output_path) as image:
                exif_dict = piexif.load(output_path)
                # exif_dict['Exif'][piexif.ImageIFD.DateTime] = created_time.strftime('%Y-%m-%d %H:%M:%S')
                # '2023: 03: 15 05: 11: 51'
                exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = created_time.strftime('%Y: %m: %d %H: %M: %S')
                exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = created_time.strftime('%Y: %m: %d %H: %M: %S')
                exif_bytes = piexif.dump(exif_dict)
                image.save(output_path, 'tiff', exif= exif_bytes)
                
            update_progress(window[CIRCULAR_PROGRESS], progress)
            setState(window, 'Extracting(' + str(finish_frame_cnt) +'/' + str(total_frames) +' images completed)')
            finish_frame_cnt = finish_frame_cnt + 1
            currentFrame = currentFrame + 1
            
            if finish_frame_cnt > total_frames:
                break
            
    window.write_event_value(FINISHED_EXTRACT, True)
    return

def update_progress(graph_elem, percent_complete) :
    """
    Update a circular progress meter
    :param graph_elem:              The Graph element being drawn in
    :type graph_elem:               sg.Graph
    :param percent_complete:        Percentage to show complete from 0 to 100
    :type percent_complete:         float | int
    """
    graph_elem.erase()
    arc_length = percent_complete/100*360+.9
    if arc_length >= 360:
        arc_length = 359.9
        
    graph_elem.draw_arc((CIRCLE_LINE_WIDTH, GRAPH_SIZE[1] - CIRCLE_LINE_WIDTH), 
                        (GRAPH_SIZE[0] - CIRCLE_LINE_WIDTH, CIRCLE_LINE_WIDTH), 
                        arc_length, 0, style='arc', arc_color=LINE_COLOR, line_width=CIRCLE_LINE_WIDTH)
    percent = percent_complete
    
    graph_elem.draw_text(f'{percent:.0f}%', TEXT_LOCATION, 
                         font=(TEXT_FONT, -TEXT_HEIGHT), color=TEXT_COLOR)
    
def setState(window, state = ""):
    window[STAT_MAIN].update(state)

def analyse_video(window, filePath) :
    detectionObjects = []
        
    # Check video file is valid
    video = cv.VideoCapture(filePath)
    if not video.isOpened():
        return
    
    totalFrame = int(video.get(cv.CAP_PROP_FRAME_COUNT))
    currentFrame = 1
    ret, frame = video.read()
    while ret:
        ret, frame = video.read()
        progress = currentFrame * 100 / totalFrame
        if frame is None:
            update_progress(window[CIRCULAR_PROGRESS], progress)
            setState(window, 'Anaylising Videos...(' + str(currentFrame) +'/' + str(totalFrame) +' images completed)')
            detectionObjects.append([])
            currentFrame = currentFrame + 1
            continue
            
        wSize = frame.shape
        width = 600
        height = 480
        
        sPoint = int(width*17.5/100)
        ePoint = int(width*82.5/100)
        
        frame = cv.resize(frame,(width,height))
        detectFrame = frame[0:height, sPoint:ePoint]
        ret = objectDetection(detectFrame)
        detectionObjects.append(ret[1])
        if len(ret[1]):
            detectedFrameList.append(str(currentFrame).zfill(8))
        update_progress(window[CIRCULAR_PROGRESS], progress)
        setState(window, 'Analying Videos...(' + str(currentFrame) +'/' + str(totalFrame) +' images completed)')
        currentFrame = currentFrame + 1
    window.write_event_value(FINISHED_ANALYSE, detectionObjects)

def objectDetection(image) :
    detectedImage = image
    recog = recognizer.detectObjectsFromImage(image, detectedImage, "array", 30, True, True)

    # for eachObject in result:
    #     print(eachObject["name"] , " : ", eachObject["percentage_probability"], " : ", eachObject["box_points"] )
    #     print("--------------------------------")
    return recog

def get_image_from_frame(frame, width, height, color):
    sPoint = int(width*17.5/100)
    ePoint = int(width*82.5/100)
    
    frame = cv.resize(frame,(width,height))
            
    drawFrame = cv.rectangle(frame, (sPoint, 0), (ePoint, height) , color , 3)
    imgbytes = cv.imencode('.ppm', drawFrame)[1].tobytes()  # can also use png.  ppm found to be more efficient
    
    return imgbytes

def analyseVideo(filePath, detectObjects) : 
    is_playing = True
    
    vidFile = cv.VideoCapture(filePath)
    # ---===--- Get some Stats --- #
    num_frames = vidFile.get(cv.CAP_PROP_FRAME_COUNT)
    fps = vidFile.get(cv.CAP_PROP_FPS)
    # sg.Column([sg.Image(key=IMAGE_FRAME, expand_y=True, enable_events=True, size=(300,200))], background_color='LightBlue')
    frame_image = [[sg.Image(key=IMAGE_FRAME, enable_events=True, expand_y=True, expand_x = True, size=(400,1))]]
    frame_list = [[sg.Listbox(values = detectedFrameList, expand_y=True, size = (20,4), font=('Courier', 14),key=LIST_FRAME, background_color='#F0F0F0', enable_events=True)],
               [sg.Button('Add', enable_events=True, key=ADD_FRAME_BUTTON),
                sg.Button('Remove', enable_events=True, key=REMOVE_FRAME_BUTTON),
                sg.Button('Save', enable_events=True, key = SAVE_BUTTON)]]
    layout = [[sg.Text('Filtering Images From Video', font=(TEXT_FONT, 20))],
              [sg.Frame('',frame_image, expand_x=True, expand_y=True),
               sg.Frame('', frame_list, expand_x = True, expand_y=True, size=(200,4), relief=sg.RELIEF_FLAT)],
              [sg.Slider(range=(0, num_frames), size=(60, 10), expand_x=True,orientation='h', key=SEEK_SLIDER, enable_events = True)],
              [sg.pin(sg.Button('Previous', enable_events=True, key=PREVIOUS_BUTTON)),
               sg.pin(sg.Button('Play', enable_events=True, key=PLAY_BUTTON, visible=False)),
               sg.pin(sg.Button('Pause', enable_events=True, key=PAUSE_BUTTON)),
               sg.pin(sg.Button('Next', enable_events=True, key=NEXT_BUTTON))]]
    
    videoWindow = sg.Window('Analyse Video', layout, no_titlebar = False, grab_anywhere=True,element_justification='c', modal=True, resizable=True, finalize=True)
    
    videoWindow.set_min_size((600,400))
    # locate the elements we'll be updating. Does the search only 1 time
    image_elem = videoWindow[IMAGE_FRAME]
    slider_elem = videoWindow[SEEK_SLIDER]
    frame_list = videoWindow[LIST_FRAME]
    timeout = 1000//fps                 # time in ms to use for window reads
    
    # ---===--- LOOP through video file by frame --- #
    cur_frame = 0
    
    def update_image():
        wSize = videoWindow[IMAGE_FRAME].get_size()
        width = wSize[0]
        height = wSize[1]
        
        try :
            if len(detectObjects[cur_frame]):
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
        except:
            color = (0, 0, 255)
            
        imgbytes = get_image_from_frame(frame, width, height, color) # can also use png.  ppm found to be more efficient
        
        image_elem.update(data=imgbytes)
        
    while True:
        event, values = videoWindow.read(timeout = timeout)
        
        if event in (None, 'Exit'):
            print("[LOG] Clicked Exit!")
            break
        
        if event == PLAY_BUTTON :
            videoWindow[PLAY_BUTTON].update(visible=False)
            videoWindow[PAUSE_BUTTON].update(visible=True)
            is_playing = True
        
        if event == PAUSE_BUTTON :
            videoWindow[PLAY_BUTTON].update(visible=True)
            videoWindow[PAUSE_BUTTON].update(visible=False)
            is_playing = False
            
        if event == NEXT_BUTTON:
            if cur_frame >= num_frames:
                return
            is_playing = False
            cur_frame = cur_frame + 1
            
            vidFile.set(cv.CAP_PROP_POS_FRAMES, cur_frame)
            ret, frame = vidFile.read()
            if not ret:
                continue
            
            update_image()
            slider_elem.update(cur_frame)
            
        if event == PREVIOUS_BUTTON:
            if cur_frame == 0:
                return;
            is_playing = False
            cur_frame = cur_frame - 1
            
            vidFile.set(cv.CAP_PROP_POS_FRAMES, cur_frame)
            ret, frame = vidFile.read()
            if not ret:
                continue
            
            update_image()
            slider_elem.update(cur_frame)
        
        if event == LIST_FRAME and len(values[event]):
            value = values[event]
            cur_frame = int(value[0])
            vidFile.set(cv.CAP_PROP_POS_FRAMES, cur_frame)
            ret, frame = vidFile.read()
            is_playing = False
            update_image()
            slider_elem.update(cur_frame)
            
        if event == SEEK_SLIDER :
            is_playing = False
            if int(values[SEEK_SLIDER]) != cur_frame-1:
                cur_frame = int(values[SEEK_SLIDER])
                vidFile.set(cv.CAP_PROP_POS_FRAMES, cur_frame)
                ret, frame = vidFile.read()
                if not ret:
                    continue
                
                update_image()
                slider_elem.update(cur_frame)
            
        if event == ADD_FRAME_BUTTON:
            detectedFrameList.append(str(cur_frame).zfill(8))
            detectedFrameList.sort()
            frame_list.update(detectedFrameList)

        if event == REMOVE_FRAME_BUTTON:
            if is_playing:
                return
            val = frame_list.get()[0]
            detectedFrameList.remove(val)
            frame_list.update(detectedFrameList)
            
        if event == SAVE_BUTTON:
            ch = sg.popup_ok_cancel("Will you save these images in the list?", "Please confirm once more.",  title="Confirm!")
            if ch=="OK":
                videoWindow.close()
                return detectedFrameList
                print ("You pressed OK")
            if ch=="Cancel":
                print ("You pressed Cancel")
            
        if is_playing == True:
            ret, frame = vidFile.read()
            if not ret:
                continue
            
            val = str(cur_frame).zfill(8)
            if val in detectedFrameList:
                frame_list.set_value(val)
            
            update_image()
            slider_elem.update(cur_frame)
            # print(detectionObjects[cur_frame])
            cur_frame += 1
    return []
    
def main():
    cv.ocl.setUseOpenCL(True)
    
    layout = [[sg.Text('Video File:', font = (TEXT_FONT, 12)), 
               sg.Input(enable_events=True, font=(TEXT_FONT, 12), expand_x=True, readonly = True,key=VIDEO_INPUT), 
               sg.FileBrowse(file_types=(('MP4 Files', "*.mp4"),('MOV Files', "*.mov"), ("All Files", '*.*')))],
              [sg.Input(enable_events=True, key=EXTRACT_ALL, visible = False),
               sg.FolderBrowse('Extract All',enable_events=True, target=EXTRACT_ALL, key = EXTRACT_ALL_BUTTON),
               sg.Button('Start Analyse', enable_events=True, key=ANALYSE_BUTTON)],
              [sg.Graph(GRAPH_SIZE, (0,0), GRAPH_SIZE, key=CIRCULAR_PROGRESS)],
              [sg.StatusBar('Please open video first                                             ', font=(TEXT_FONT, 11), key=STAT_MAIN, expand_x=True, background_color='grey')]]
    
    window =sg.Window('Clip Images', layout, no_titlebar=False, grab_anywhere=True, element_justification='c')
    
    sg.theme('LightBlue')    
    
    file = ""
    folder = ""
    saveThread = None
    while True:
        event, values = window.read(timeout = 100)
        
        if event in (None, 'Exit'):
            print("[LOG] Clicked Exit!")
            break
        
        if event == EXTRACT_ALL:
            if file == "":
                setState(window, "Please open video first")
                continue
            
            window[ANALYSE_BUTTON].update(disabled = True)
            setState(window, 'start extracting....')
            folder = values[event]
            saveThread = Thread(target=extract_video,args=(window, file, folder), daemon=True)
            saveThread.start()
            window[EXTRACT_ALL_BUTTON].update(disabled = True)
            # extract_video(window, file, save_path)
            # break;
            
        if event == VIDEO_INPUT:
            file = values[VIDEO_INPUT]
            
            # Verify video file is valid
            video = cv.VideoCapture(file)
            if not video.isOpened():
                sg.popup_error('Video File is invalid! Please open another file',title = 'Error')
                setState(window,'Fail to open video file')
                continue

            setState(window, 'Success to Open Video File...')
            
        if event == ANALYSE_BUTTON:
            if file == "":
                setState(window, "Please open video first")
                continue
            detectedFrameList = []
            window[ANALYSE_BUTTON].update(disabled = True)
            window[EXTRACT_ALL_BUTTON].update(disabled = True)
            analyseThread = Thread(target=analyse_video,args=(window, file), daemon=True)
            analyseThread.start()
        
        if event == FINISHED_ANALYSE:
            detectObjects = values[event]
            save_frames = analyseVideo(file,detectObjects)
            if len(save_frames) == 0:
                window[ANALYSE_BUTTON].update(disabled = False)
                window[EXTRACT_ALL_BUTTON].update(disabled = False)
            else:
                folder=sg.popup_get_folder('Get folder', title="Select folder to save Images")
                print ("Folder selected",folder)
                saveThread = Thread(target=extract_video,args=(window, file, folder, save_frames), daemon=True)
                saveThread.start()
            
        if event == FINISHED_EXTRACT:
            window[ANALYSE_BUTTON].update(disabled = False)
            window[EXTRACT_ALL_BUTTON].update(disabled = False)
main()
