# Auto-Mux


## What’s it for?

Batch muxing (remapping video/audio streams without rerendering) via the Win Explorer context menu.


## Why?

The muxing utilities I tried prior had lots of other useful features that I didn’t use and got in the way, clunky GUIs and limited/complicated batching capabilities. 

I work for a company that provides an online school open day platform. Redoing renders for the platform’s flythroughs are incredibly processor intensive and time-consuming. Often clients elect to have narration or a backing music track after their flythroughs are deployed. The naming structure for the files that are exported from our NLE is always: “schoolName_tourName_pointNumber_renderType.mxf”

By simply cutting the audio track against the existing NLE project and exporting the audio only, we can select those files in explorer, right click > send to > Auto-Mux, and batch mux by matching the “pointNumber” between video and audio streams. This saves the pain of rerendering everything.


### Yeah well that sounds okay, but how would that help me?

If batch muxing from the explorer context menu would be useful to you but you want to tweak the settings a bit, simply edit the variables at the top of the “Auto-Mux.py” file. They should be pretty self explanatory.


# Requirements



*   Windows only, tested on Windows 10
*   Tested on Python 3.6 + 3.7.4
*   Requires FFMPEG to be installed and accessible in PATH
*   No additional python packages necessary, but install colorama if coloured output is desirable.


# Setup



1. Install FFMPEG and add it to PATH environment variable
2. Download Auto-Mux, put it wherever you like
3. Run Setup.bat to create a shortcut in Send To


# User variables


### _regex_criteria = "^(p\d+)"_

Common denominator between matching video/audio streams. In this case the literal letter ‘p’ followed by one digit or more.


### _match_as_video_type = [".mp4", ".mov"]_

A list of extensions that will be detected as video files. There is no mime-type detection built into Auto-Mux. If a file’s literal extension is “.mp4” or “.mov” it will be passed for muxing.


### _match_as_audio_type = [".wav", ".aac"]_

A list of extensions that will be detected as video files. There is no mime-type detection built into Auto-Mux. If a file’s literal extension is “.mp4” or “.mov” it will be passed for muxing.


### _muxed_suffix = "_muxed"_

Output file suffix, ignored if _post_cleanup_ is **True**


### match_limit = 2 

This allows an audio track to match a videostream as a muxing candidate multiple times. Ideal if you have multiple identical videos with different resolutions. Set to 1 to disable. There is no option for the inverse; matching multiple audio files to a single video file. 


### post_cleanup = True

If set to true, automatically tidies processed files into subfolders. If enabled, files are renamed to their original pre-muxed counterparts, effectively ignoring _muxed_suffix_.


### write_log = True

Keep a changelog of processed files


### custom_log_path = ""

Leave as "" to log into the same directory as muxed files.


### video_tidy = "OLD"

A subfolder to put processed video files into.

Can be set to same as _audio_tidy._

Ignored if _post_cleanup _is false


### audio_tidy = "Audio"

A subfolder to put processed audio files into.

Can be set to same as _video_tidy._

Ignored if _post_cleanup _is false
