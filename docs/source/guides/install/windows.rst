Windows
--------------
From powershell, run:

.. code-block:: powershell

  # Download ffmpeg/ffprobe dependencies from yt-dlp
  curl.exe -L -o ffmpeg.zip https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
  tar -xf ffmpeg.zip
  move "ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" "ffmpeg.exe"
  move "ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe" "ffprobe.exe"

  # Download ytdl-sub
  curl.exe -L -o ytdl-sub.exe https://github.com/jmbannon/ytdl-sub/releases/latest/download/ytdl-sub.exe
  ytdl-sub.exe -h