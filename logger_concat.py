import os
from pydub import AudioSegment as combine
from datetime import datetime, timedelta

var LOGGER_LOCATION = "Network\10.0.0.210\Logger\audiohi"

def get_file_names(directory, start_time, end_time):
    files = [f for f in os.listdir(LOGGER_LOCATION) if f.endswith('.wav')]
    file_list = []
    for file in files:
        timestamp_str = file.split('.')[0]
        timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M')
        file_list.append((timestamp, file))
        
    file_list.sort()
    linked_list = file_list
        
    start_file = min(file_list, key=lambda x: abs(x[0] - start_time))
    end_file = min(file_list, key=lambda x: abs(x[0] - end_time))
        
    start_index = file_list.index(start_file)
    end_index = file_list.index(end_file)
        
    files_to_concat = [f[1] for f in file_list[start_index:end_index+1]]
        
    return files_to_concat, linked_list