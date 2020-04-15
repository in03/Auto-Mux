
import os, sys, time
import pathlib
import shutil
import re
import argparse
import subprocess

# Coloured stdout
try:
    from colorama import Fore
except ImportError:
    Fore.RED = ""
    Fore.YELLOW = ""
    Fore.GREEN = ""
    print("Install Colorama module for coloured console output")
    time.sleep(3)

################ USER VARIABLES #################

# What to look for to match tracks
# In this case match a point number, "p" followed by one or more numbers
# E.g, 'p1' in 'ProjectName_SequenceName_p1l_RenderType.mp4'
regex_criteria = "^(p\d+)"

# List video/audio types you want to identify for muxing here
match_as_video_type = [".mp4", ".mov"]
match_as_audio_type = [".wav", ".aac"]

# Output file suffix, ignored if post_cleanup is True
muxed_suffix = "_muxed"

# If muxing an audio track to multiple identical videos of differing resolutions
# Set to 1 to remove an audio track as a possible match
match_limit = 2 

# Tidy up used files into subfolders? True/False
post_cleanup = True

# Write a log of processed files?
write_log = True

# Leave as "" to log into the output file directory
# This means an incorrect path will fail silently
custom_log_path = ""

# Folders to tidy up into
# Set to same if desired
video_tidy = "OLD"
audio_tidy = "Audio"

###############################################
################ FUNCTIONS ####################

def sort_media_types(file_list):
    '''Sort media types based on user variables
    into video, audio and unsupported lists'''
    videoList = []
    audioList = []
    unsupportedList = []

    for media in file_list:
        mediaExt = os.path.splitext(media)[1]
        if mediaExt.lower() in match_as_video_type:
            videoList.append(media)
        elif mediaExt.lower() in match_as_audio_type:
            audioList.append(media)
        else:
            print(f"{media} is unsupported. Skipping.")
            unsupportedList.append(media)
    return [videoList, audioList, unsupportedList]

###############################################

def match_and_mux(videoList, audioList):

    audioCount = {}
    outputList = []
    failed_regex = []

    for video in videoList:
        print(Fore.GREEN + video)
        match = re.match(regex_criteria, os.path.basename(video))[0]
        if not match:
            failed_regex.append(video)
            print(Fore.YELLOW + f"{video} failed regex match. Skipping.")
            continue

        print(Fore.GREEN + f"VIDEO CRITERIA MATCH: {match}")
        for audio in audioList:
            print(Fore.GREEN + f" AUDIO: {audio}")
            if str(match) in str(os.path.basename(audio)):
                print(Fore.GREEN + os.path.basename(audio))
                
                outputPath = f"{os.path.splitext(video)[0]}{muxed_suffix}{os.path.splitext(video)[1]}"
                outputList.append(outputPath)
                print(f"Processing: \"{outputPath}\"")
                if audio not in audioCount:
                    audioCount[audio] = 1
                elif audioCount == match_limit:
                    # For our use case, audio should only match twice.
                    # E.g., p1l, p1s
                    audioList.remove([audio])
                    print(f"{audioList[audio]} has now been used {match_limit} times.")
                else:
                    audioCount[audio] +=1
                        # Mux with ffmpeg.
                subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-i", audio, "-ac", "2", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-map", "0:v:0", "-map", "1:a:0", outputPath], stdout=subprocess.PIPE)              
    return [audioCount, outputList]

###############################################
  
def cleanup_used_files(list, subfolder_name):  
    '''Cleanup files into a subfolder of the files parent path'''      
    for file in list:
        subfolder = os.path.dirname(file) + "\\" + subfolder_name
        if not os.path.exists(subfolder):
            try:
                os.mkdir(subfolder)
            except IOError:
                print(Fore.YELLOW + f"Couldn't make \"{subfolder_name}\" subfolder, skipping...")
                return False
        try:
            shutil.move(file, (subfolder + "\\" + os.path.basename(file)))
        except IOError:
            print(Fore.YELLOW + f"Couldn't move \"{file}\", skipping...")
            return False

###############################################

if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs='+')
    args = parser.parse_args()
    file_list = args.file

    if len(file_list) < 2:
        print("Not enough files passed")
        sys.exit(1)

    # Sort media types
    videoList, audioList, unsupportedList = sort_media_types(file_list)

    # Check muxable streams
    if len(videoList) == 0 and len(audioList) == 0:
        print("No valid video or audio streams passed for muxing. Check your selection.")
        sys.exit(1)

    if len(videoList) == 0:
        print("No valid video streams passed for muxing. Check your selection.")
        sys.exit(1)

    if len(audioList) == 0:
        print("No valid audio streams passed for muxing. Check your selection.")
        sys.exit(1)


    # Match media and mux
    audioCount, outputList = match_and_mux(videoList, audioList)

    # Cleanup       
    
    if post_cleanup:
        if cleanup_used_files(audioList, audio_tidy):
            print(Fore.RED + "Couldn't tidy up used audio files")

        if cleanup_used_files(videoList, video_tidy):
            print(Fore.RED + "Couldn't tidy up used video files.")

        # Rename muxed files
        renamed_muxed = []

        for outputFile in outputList:
            output_dir = os.path.dirname(outputFile)
            split_ext = os.path.splitext(os.path.basename(outputFile))
            new_name = split_ext[0][0:-6]
            new_name = f"{output_dir}\\{new_name}{split_ext[1]}"
            renamed_muxed.append(new_name)
            try:
                os.rename(outputFile, new_name)
            except IOError:
                print(Fore.YELLOW + f"Could not rename {outputFile}, skipping.")


    # Status Report
    unmatched_audio = [x for x in audioList if x not in audioCount]
    if post_cleanup:
        outputList = renamed_muxed
    unmatched_video = [x for x in videoList if x not in outputList]

    if len(unsupportedList) != 0:
        print(f"failed {len(unsupportedList)} files for wrong filetype. Check changelog.")

    if len(unmatched_audio) !=0:
        print(f"{len(unmatched_audio)} audio files did not have a match. Check changelog.")

    if len(unmatched_video) !=0:
        print(f"failed {len(unmatched_video)} video files did not have a match. Check changelog.")
    


    # Write Changelog

    parent_dir = os.path.dirname(outputList[0])
    if write_log:
        try:
            if os.path.exists(custom_log_path):
                log_path = custom_log_path
            else:
                log_path = parent_dir
        except:
            log_path = parent_dir
                

        changelog = open(log_path + "\\Auto Mux Changelog.log", "w+")

        changelog.write("Succesfully muxed:\n")
        for muxed in outputList:
            changelog.write(muxed + "\n")

        changelog.write("Skipped incompatible files:\n")
        for failed in unsupportedList:
            changelog.write(failed + "\n")

        changelog.write("These audio files did not have a match: \n")
        for audio in unmatched_audio:
            changelog.write(audio + "\n")

        changelog.write("These video files did not have a match: \n")
        for video in unmatched_video:
            changelog.write(video + "\n")

        changelog.close()