## TODO
A sloppy todo list file where I write any issues/things to address that pop in my head
- Add more tests with coverage
- Validate output paths work before downloading
- Maintain playlist ordering
  - Suppose you download a YT playlist and you want the ordering in your filenames. Then someone edits the playlist by deleting a video, changing order, etc. How do you deal with that?
  - A few ideas:
    - Do not let users use order_index, instead, rely on the upload date for ordering.
    - `naive strict` - if the playlist order is different, delete and redownload the whole thing
      - Would lose videos that got deleted/hidden
    - `strict` - if the playlist order is different, move existing files into working directory, rename to {id}.{ext}, and re-post-process using downloaded .info.json
      - How would you post-process a deleted video?
      - Store .info.json alongside the file, move it to a deleted videos location?
    - `loose` - maintain order based on when it was downloaded in ytdl-sub
      - Would need to keep track of a counter for the playlist
      