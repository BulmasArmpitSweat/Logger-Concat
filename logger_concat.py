import os
import shutil
from pydub import AudioSegment
from datetime import datetime, timedelta

LOGGER_LOCATION = r"\\10.0.0.210\Logger\audiohi"
TEMPORARY_LOCATION = "."

def print_help():
    print("Commands you can use:\n")
    print("    help        | Print this message\n")
    print("    concatenate | Concatenate audio files within a specified time range\n")
    print("        [dd-mm-yyyy hh:mm -> dd-mm-yyyy hh:mm] or,\n")
    print("        [from dd-mm-yyyy hh:mm to dd-mm-yyyy hh:mm]\n")
    print("    logg        | Print helpful information about the logger folder\n")
    print("    exit        | Exit the CLI interface, and thus the program")

def move_files(files):
    moved_files = []
    print("\n")
    for index, file in enumerate(files, start=1):
        print(f"\rProcessing file {index}")
        original_path = os.path.join(LOGGER_LOCATION, file)
        if not os.path.exists(original_path):
            print(f"File {file} does not exist.")
            continue

        new_path = os.path.join(TEMPORARY_LOCATION, file)
        if file.endswith(".mp3"):
            try:
                audio = AudioSegment.from_mp3(original_path)  # Load the .mp3 file
                new_path = new_path.replace(".mp3", ".wav")  # Change extension to .wav
                audio.export(new_path, format="wav")  # Convert to .wav and save
                moved_files.append(new_path)
                print(f"Converted {file} to {new_path}")
            except Exception as e:
                print(f"Error converting {file}: {e}")
        elif file.endswith(".wav"):
            try:
                shutil.move(original_path, new_path)
                moved_files.append(new_path)
            except Exception as e:
                print(f"Error moving file {file}: {e}")
    return moved_files

def resolve_cli_input(command_array):
    try:
        if command_array[1] == 'from':
            start_time = datetime.strptime(command_array[2] + ' ' + command_array[3], '%d-%m-%Y %H:%M')
            end_time = datetime.strptime(command_array[5] + ' ' + command_array[6], '%d-%m-%Y %H:%M')
        else:
            start_time = datetime.strptime(command_array[1] + ' ' + command_array[2], '%d-%m-%Y %H:%M')
            end_time = datetime.strptime(command_array[4] + ' ' + command_array[5], '%d-%m-%Y %H:%M')
    except ValueError as e:
        print(f"Error parsing dates: {e}")
        return None, None
    return start_time, end_time

def get_file_names(directory, start_time, end_time):
    files = [f for f in os.listdir(directory) if f.endswith('.wav')]
    file_list = []
    for file in files:
        timestamp_str = file.split('.')[0]
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M')
        except ValueError:
            print(f"Skipping invalid file timestamp: {file}")
            continue
        file_list.append((timestamp, file))
        
    if not file_list:
        return [], []

    file_list.sort()
    start_file = min(file_list, key=lambda x: abs(x[0] - start_time), default=(None, None))
    end_file = min(file_list, key=lambda x: abs(x[0] - end_time), default=(None, None))
    
    if start_file[0] is None or end_file[0] is None:
        print("No files found in the specified range.")
        return [], []
        
    start_index = file_list.index(start_file)
    end_index = file_list.index(end_file)
        
    files_to_concat = [f[1] for f in file_list[start_index:end_index+1]]
        
    return files_to_concat, file_list

def concatenate_audio_files(files, directory):
    combined = AudioSegment.empty()
    for file in files:
        try:
            audio = AudioSegment.from_wav(os.path.join(directory, file))
            combined += audio
        except Exception as e:
            print(f"Error processing file {file}: {e}")
    return combined

if __name__ == "__main__":
    directory = LOGGER_LOCATION
    if not os.path.exists(directory):
        print("ERROR: Cannot access the Logger folder. Is this being run on the right computer?\n")
        exit(1)

    while True:
        print(": ", end="")
        command = input().split()
        if not command:
            continue
        if command[0] == "help":
            print_help()
        elif command[0] == "concatenate":
            start_time, end_time = resolve_cli_input(command)
            if not start_time or not end_time:
                continue
            files_to_concat, linked_list = get_file_names(directory, start_time, end_time)
            if not files_to_concat:
                print("No files found to concatenate.")
                continue
            print(f"Combining files from {start_time} to {end_time}\n")
            for timestamp, filename in linked_list:
                print(f"{timestamp}: {filename}\n")
            print("Moving files to temporary location...\n")
            moved_files = move_files(files_to_concat)
            print("Combining audio data...\n")
            combined_audio = concatenate_audio_files(moved_files, TEMPORARY_LOCATION)
            output_filename = datetime.now().strftime('%Y%m%d%H%M') + '.wav'
            print("Exporting final audio file...\n")
            combined_audio.export(os.path.join(TEMPORARY_LOCATION, output_filename), format="wav")
            print("Deleting files...\n")
            for deleted_files, file in enumerate(moved_files, start=1):
                print(f"Deleting file {deleted_files}")
                try:
                    os.remove(file)
                except Exception as e:
                    print(f"Error deleting file {file}: {e}")
        elif command[0] == "logg":
            files = [f for f in os.listdir(directory) if f.endswith('.wav')]
            if not files:
                print("No files found in the folder.")
            else:
                file_list = []
                for file in files:
                    timestamp_str = file.split('.')[0]
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M')
                    except ValueError:
                        print(f"Skipping invalid file timestamp: {file}")
                        continue
                    file_list.append((timestamp, file))
                file_list.sort()
                earliest_file_time = file_list[0][0]
                newest_file_time = file_list[-1][0]
                print(f"Total files: {len(files)}\n")
                print(f"Starting at {earliest_file_time}, and running through to {newest_file_time}\n")
                print("NOTE: newest file may be incomplete, as the logger is continuously writing to this directory\n")
        elif command[0] == "exit":
            break
        else:
            print(f"Invalid command. {command[0]} is not a valid command. Hint: type 'help' for a list of commands.")
    exit(0)
