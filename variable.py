# Settings to modify elements
GRAPH_SIZE = (100, 100)                             # Size of the progress bar
CIRCLE_LINE_WIDTH, LINE_COLOR = 12, 'yellow'        # Size of circle width and color
# Text Setting in Progress bar
TEXT_COLOR = 'black'                                # Color of the progress value
TEXT_HEIGHT = GRAPH_SIZE[0]//4
TEXT_LOCATION = (GRAPH_SIZE[0]//2, GRAPH_SIZE[1]//2)

TEXT_FONT = 'Helvetica'         # Fonts of the text

PATH_MODEL = 'tiny-yolov3.pt'

# Winodw IDs
IMAGE_FRAME = '-IMAGE-'
LIST_FRAME = '-FRAME_LIST-'
SEEK_SLIDER = '-SLIDER-'
VIDEO_INPUT = '-VIDEO_PATH-'
CIRCULAR_PROGRESS = '-GRAPH-'
STAT_MAIN = '-STAT_MAIN-'
EXTRACT_ALL = '-EXTRACT_ALL-'

# Button IDs
EXTRACT_ALL_BUTTON = '-EXTRACT_ALL_BUTTON-'
ANALYSE_BUTTON = '-ANALYSE-'

ADD_FRAME_BUTTON = '-ADD_FRAME-'
REMOVE_FRAME_BUTTON = '-REMOVE_FRAME-'
PREVIOUS_BUTTON = '-PREVIOUS_BTN-'
PLAY_BUTTON = '-PLAY_BTN-'
PAUSE_BUTTON = '-PAUSE_BTN-'
NEXT_BUTTON = '-NEXT_BTN-'
SAVE_BUTTON = '-SAVE_FRAME_BTN-'

# Event Values
FINISHED_EXTRACT = '-FINISH_EXTRACT-'
FINISHED_ANALYSE = '-ANALYSE_FINISHED-'