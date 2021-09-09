from datetime import datetime
import os
from shutil import copyfile
import urllib
import music_tag
from sanitize_filename import sanitize
import dicttoxml

from PIL import Image
from ytdl_subscribe import SubscriptionSource

import youtube_dl as ytdl

def _f(value, entry):
    return value.format(**entry)


def _ffile(file_value, path, entry, makedirs=False):
    file_name = _f(file_value, entry)
    output_file_path = f"{path}/{file_name}"
    if makedirs:
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    return output_file_path


class Subscription(object):
    WORKING_DIRECTORY = ''

    source = None

    def __init__(self, url, ytdl_opts, post_process, overrides, output_path):
        self.url = url
        self.ytdl_opts = ytdl_opts or dict()
        self.post_process = post_process
        self.overrides = overrides
        self.output_path = output_path

        # Always set outtmpl to the id and extension. Will be renamed using the subscription's output_path value
        self.ytdl_opts['outtmpl'] = self.WORKING_DIRECTORY + '/%(id)s.%(ext)s'


    def parse_entry(self, entry):
        # Add overrides to the entry
        entry = dict(entry, **self.overrides)

        # Add the file path to the entry, assert it exists
        entry['file_path'] = f"{self.WORKING_DIRECTORY}/{entry['id']}.{entry['ext']}"
        assert os.path.isfile(entry['file_path'])

        # Add sanitized values
        entry['sanitized_artist'] = sanitize(entry['artist'])
        entry['sanitized_title'] = sanitize(entry['title'])

        return entry

    def _post_process_tagging(self, entry):
        t = music_tag.load_file(entry['file_path'])
        for tag, tag_formatter in self.post_process['tagging'].items():
            t[tag] = _f(tag_formatter, entry)
        t.save()

    def _post_process_nfo(self, entry):
        nfo = {}
        for tag, tag_formatter in self.post_process['nfo'].items():
            nfo[tag] = _f(tag_formatter, entry)

        xml = dicttoxml.dicttoxml(
            obj=nfo,
            root='nfo_root' in self.post_process,
            custom_root=self.post_process.get('nfo_root'),
            attr_type=False,
        )
        nfo_file_path = _ffile(self.post_process['nfo_name'], self.output_path, entry, makedirs=True)
        with open(nfo_file_path, 'wb') as f:
            f.write(xml)

    def post_process_entry(self, entry):
        if 'tagging' in self.post_process:
            self._post_process_tagging(entry)

        # Move the file after all direct file modifications are complete
        output_file_path = _ffile(self.post_process['file_name'], self.output_path, entry, makedirs=True)
        copyfile(entry['file_path'], output_file_path)

        # Download the thumbnail if its present
        if 'thumbnail_name' in self.post_process:
            thumbnail_file_path = _ffile(self.post_process['thumbnail_name'], self.output_path, entry, makedirs=True)
            urllib.request.urlretrieve(entry['thumbnail_url'], thumbnail_file_path)
            if 'convert_thumbnail' in self.post_process:
                # TODO: Clean with yaml definitions
                if self.post_process['convert_thumbnail'] == 'jpg':
                    self.post_process['convert_thumbnail'] = 'jpeg'
                im = Image.open(thumbnail_file_path).convert("RGB")
                im.save(thumbnail_file_path, self.post_process['convert_thumbnail'])

        if 'nfo' in self.post_process:
            self._post_process_nfo(entry)

    def extract_info(self):
        """
        Extracts only the info of the source, does not download it
        """
        with ytdl.YoutubeDL(self.ytdl_opts) as ytd:
            info = ytd.extract_info(self.url)

        entries = [self.parse_entry(e) for e in info['entries']]
        for e in entries:
            self.post_process_entry(e)

        return

    @classmethod
    def from_dict(cls, d):
        source = d['source']
        if source == SubscriptionSource.SOUNDCLOUD:
            dclass = SoundcloudSubscription
        elif source == SubscriptionSource.YOUTUBE:
            dclass = YoutubeSubscription
        else:
            raise ValueError('dne')

        return dclass(
            url=d['url'],
            ytdl_opts=d['ytdl_opts'],
            post_process=d['post_process'],
            overrides=d['overrides'],
            output_path=d['output_path']
        )


class SoundcloudSubscription(Subscription):
    source = SubscriptionSource.SOUNDCLOUD

    def parse_entry(self, entry):
        entry = super(SoundcloudSubscription, self).parse_entry(entry)
        entry['upload_year'] = datetime.fromtimestamp(entry['timestamp']).year

        # Add thumbnail values
        original_thumbnail = [t for t in entry['thumbnails'] if t['id'] == 'original'][0]
        entry['thumbnail_url'] = original_thumbnail['url']
        entry['thumbnail_ext'] = original_thumbnail['url'].split('.')[-1]

        return entry


class YoutubeSubscription(Subscription):
    source = SubscriptionSource.YOUTUBE

    def parse_entry(self, entry):
        entry = super(YoutubeSubscription, self).parse_entry(entry)
        entry['upload_year'] = entry['upload_date'][:4]

        entry['thumbnail_url'] = entry['thumbnail']
        entry['thumbnail_ext'] = 'webp'

        # Try to get the track, fall back on title
        entry['sanitized_track'] = sanitize(entry.get('track', entry['title']))
        return entry