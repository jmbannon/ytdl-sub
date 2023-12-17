Linux
--------------
Requires ffmpeg as a dependency. Can typically be installed with any Linux package manager.

.. code-block:: bash

   curl -L -o ytdl-sub https://github.com/jmbannon/ytdl-sub/releases/latest/download/ytdl-sub
   chmod +x ytdl-sub
   ytdl-sub -h

You can also install using yt-dlp's ffmpeg builds. This ensures your ffmpeg is up to date:

.. code-block:: bash

   curl -L -o ffmpeg.tar.gz https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
   tar -xf ffmpeg.tar.gz
   chmod +x ffmpeg-master-latest-linux64-gpl/bin/ffmpeg
   chmod +x ffmpeg-master-latest-linux64-gpl/bin/ffprobe

   # May need sudo / root permissions to perform
   mv ffmpeg-master-latest-linux64-gpl/bin/ffmpeg /usr/bin/ffmpeg
   mv ffmpeg-master-latest-linux64-gpl/bin/ffprobe /usr/bin/ffprobe

Linux ARM
--------------
Requires ffmpeg as a dependency. Can typically be installed with any Linux package manager.

.. code-block:: bash

   curl -L -o ytdl-sub https://github.com/jmbannon/ytdl-sub/releases/latest/download/ytdl-sub_aarch64
   chmod +x ytdl-sub
   ytdl-sub -h

You can also install using yt-dlp's ffmpeg builds. This ensures your ffmpeg is up to date:

.. code-block:: bash

   curl -L -o ffmpeg.tar.gz https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz
   tar -xf ffmpeg.tar.gz
   chmod +x ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg
   chmod +x ffmpeg-master-latest-linuxarm64-gpl/bin/ffprobe

   # May need sudo / root permissions to perform
   mv ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg /usr/bin/ffmpeg
   mv ffmpeg-master-latest-linuxarm64-gpl/bin/ffprobe /usr/bin/ffprobe