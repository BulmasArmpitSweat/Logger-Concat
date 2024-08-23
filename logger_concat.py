import os
import shutil
from pydub import AudioSegment
from datetime import datetime, timedelta

LOGGER_LOCATION: str = r"Network\10.0.0.210\Logger\audiohi"
TEMPORARY_LOCATION: str = "."

def print_help():
    print("Commands you can use:\n\n")
    print("    help        | Print this message\n")
    print("    concatenate |\n")
    print("        [dd-mm-yyyy hh:mm -> dd-mm-yyyy hh:mm] or,\n")
    print("        [from dd-mm-yyyy hh:mm to dd-mm-yyyy hh:mm]\n")
    print("         eg: 23-08-2024 10:00 -> 23-08-2024 13:00 | or,\n")
    print("         eg: from 23-08-2024 10:00 to 23-08-2024 13:00\n")
    print("    logg        | Print helpful information about the logger folder\n")
    print("    exit        | Exit the CLI interface, and thus the program")
def move_files(files):
    moved_files_index = 1
    moved_files = []
    print("\n")
    for file in files:
        print(f"\rMoving file {moved_files_index}")
        original_path = os.path.join(LOGGER_LOCATION, '\\', file)
        new_path      = os.path.join(TEMPORARY_LOCATION, '\\', file)
        shutil.move(original_path, new_path)
        moved_files.append(new_path)
        moved_files_index += 1
    return moved_files

def resolve_cli_input(command_array):
    start_time = None
    end_time = None
    if (command_array[1] == 'from'):
        start_time = datetime.strptime(command_array[2] + ' ' + command_array[3], '%d-%m-%Y %H:%M')
        end_time   = datetime.strptime(command_array[5] + ' ' + command_array[6], '%d-%m-%Y %H:%M')
    else:
        start_time = datetime.strptime(command_array[1] + ' ' + command_array[2], '%d-%m-%Y %H:%M')
        end_time   = datetime.strptime(command_array[4] + ' ' + command_array[5], '%d-%m-%Y %H:%M')
    return start_time, end_time

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

def concatenate_audio_files(files):
    combined = AudioSegment.empty()
    for file in files:
        audio = AudioSegment.from_wav(os.path.join(directory, file))
        combined += audio
    return combined

if __name__ == "__main__":
    directory = LOGGER_LOCATION
if not os.path.exists(directory):
    print("ERROR: Cannot access the Logger folder. Is this being run on the right computer?\n")
    exit(1)

    while 1:
        print(": ")
        command = input().split()
        if not command:
            continue
        match command[0]:
            case "help":
                print_help()
            case "concatenate":
                start_time, end_time = resolve_cli_input(command)
                files_to_concat, linked_list = get_file_names(LOGGER_LOCATION, start_time, end_time)
                print(f"Combining files from {start_time} to {end_time}\n")
                for timestamp, filename in linked_list:
                    print(f"{timestamp}: {filename}\n")
                print("Moving files to temporary location...\n")
                moved_files = move_files([f[1] for f in linked_list])
                print("Combining audio data...\n")
                combined_audio = concatenate_audio_files(moved_files)
                output_filename = datetime.now().strftime('%Y%m%d%H%M') + '.wav'
                print("Exporting final audio file...\n")
                combined_audio.export(os.path.join(TEMPORARY_LOCATION, output_filename), format="wav")
                deleted_files = 1
                print("\n")
                for file in moved_files:
                    print(f"Deleting file {deleted_files}")
                    os.remove(file)
                    deleted_files += 1
            case "logg":
                files = [f for f in os.listdir(LOGGER_LOCATION) if f.endswith('.wav')]
                if not files:
                    print("Could not access folder. Is this being run on the right computer?\n")
                else:
                    file_list = []
                    for file in files:
                        timestamp_str = file.split('.')[0]
                        timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M')
                        file_list.append((timestamp, file))
                    file_list.sort()

                    earliest_file_time = file_list[0][0]
                    newest_file_time = file_list[-1][0]

                    print(f"Total files: {len(files)}\n")
                    print(f"Starting at {earliest_file_time}, and running through to {newest_file_time}\n")
                    print("NOTE: newest file may be incomplete, as the logger is continuously writing to this directory\n")
            case "exit":
                break
            case _:
                print(f"Invalid command. {command[0]} is not a valid command. Hint: type 'help' for a list of commands.")
exit(0)
