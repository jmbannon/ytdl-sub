import pytest

from ytdl_sub.utils.chapters import Chapters
from ytdl_sub.utils.chapters import Timestamp


class TestTimestamp:
    @pytest.mark.parametrize(
        "timestamp_str, timestamp_int",
        [
            ("0:00", 0),
            ("0:24", 24),
            ("1:11", 71),
            ("01:11", 71),
            ("00:22", 22),
            ("1:01:01", 3600 + 60 + 1),
            ("01:01:01", 3600 + 60 + 1),
            ("00:00:00", 0),
        ],
    )
    def test_timestamp_from_str(self, timestamp_str, timestamp_int):
        ts = Timestamp.from_str(timestamp_str=timestamp_str)
        assert ts.timestamp_sec == timestamp_int


@pytest.fixture
def chapter_description_1() -> str:
    return """Support the artist by purchasing the record here:
https://levanika.bandcamp.com/album/p...

Album Art by: po

Tracklist:
00:00 intro
00:58 audioclip p94568
01:18 saskipao
03:32 fifqeby
05:40 dream
07:22 rulji
08:54 modymody
11:23 .ishos
16:09 pos
18:47 lamazybalaxy

Denivarlevy Socials:

https://open.spotify.com/artist/2XdIT...
https://youtube.com/channel/UCgI_vAC3...
"""


@pytest.fixture
def chapter_description_2() -> str:
    return """01. 00:00 Ocean 
02. 02:41 Dreams 
03. 05:16 Future Tales 
04. 08:50 Mind Travelling 
05. 11:05 Love Supreme 
06. 14:17 Reflections 
07. 16:32 Moonlight Fading 
08. 19:40 Between Two Worlds
"""

@pytest.fixture
def chapter_description_3() -> str:
    return """Tracklist Nightcore :
00:00 (Nightcore) Cartoon - On & On (feat. Daniel Levi)
03:02 (Nightcore) Cartoon - Why We Lose (feat. Coleman Trapp)
06:09 (Nightcore) Vanze - Forever (feat. Brenton Mattheus)
09:49 (Nightcore) Krale - Frontier (ft. Jasmina Lin & Jay Christopher)
13:11 (Nightcore) Jim Yosef - Forces (feat. Ivan Jamile & Kédo Rebelle)
17:01 (Nightcore) Janji - Heroes Tonight (feat. Johnning)
20:02 (Nightcore) Jim Yosef - Can't Wait (feat. Anna Yvette)
23:01 (Nightcore) Ship Wrek & Zookeepers - Ark 
26:00 (Nightcore) Electro-Light & Jordan Kelvin James - Wait For You (feat. Anna Yvette)
29:28 (Nightcore)  JJD - Adventure
34:19 (Nightcore) Halvorsen - She Got Me Like
36:42 (Nightcore) Desmeon - Hellcat
40:27 (Nightcore) Rameses B - Beside You (feat. Soundr) 
44:46 (Nightcore) Axol - ILY
47:40 (Nightcore) ElementD - Fallin' (feat. Micah Martin) 
50:24 (Nightcore) Futuristik - Little Bit (feat. Sethh)
54:39 (Nightcore) IZECOLD - Close (feat. Molly Ann)
57:20 (Nightcore) Chime & Adam Tell - Whole
"""

class TestChapters:
    def test_chapters_from_str_1(self, chapter_description_1):
        chapters = Chapters.from_string(chapter_description_1)
        assert len(chapters) == 10
        assert chapters.timestamps[-1].readable_str == "18:47"

    def test_chapters_from_str_2(self, chapter_description_2):
        chapters = Chapters.from_string(chapter_description_2)
        assert len(chapters) == 8
        assert chapters.timestamps[1].readable_str == "2:41"

    def test_chapters_from_str_3(self, chapter_description_3):
        chapters = Chapters.from_string(chapter_description_3)
        assert len(chapters) == 18
        assert chapters.titles[8] == '(Nightcore) Electro-Light & Jordan Kelvin James - Wait For You (feat. Anna Yvette)'
