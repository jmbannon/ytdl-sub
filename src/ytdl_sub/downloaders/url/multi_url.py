from typing import Dict
from typing import List

from ytdl_sub.downloaders.url.downloader import BaseUrlDownloader
from ytdl_sub.downloaders.url.downloader import DownloaderValidator
from ytdl_sub.downloaders.url.validators import MultiUrlValidator


class MultiUrlDownloadOptions(MultiUrlValidator, DownloaderValidator):
    """
    Downloads from multiple URLs. If an entry is returned from more than one URL, it will
    resolve to the bottom-most URL settings.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          download:
            # required
            download_strategy: "multi_url"
            urls:
              - url: "youtube.com/channel/UCsvn_Po0SmunchJYtttWpOxMg"
                variables:
                  season_index: "1"
                  season_name: "Uploads"
                playlist_thumbnails:
                  - name: "poster.jpg"
                    uid: "avatar_uncropped"
                  - name: "fanart.jpg"
                    uid: "banner_uncropped"
                  - name: "season{season_index}-poster.jpg"
                    uid: "latest_entry"
              - url: "https://www.youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg"
                variables:
                  season_index: "2"
                  season_name: "Playlist as Season"
                playlist_thumbnails:
                  - name: "season{season_index}-poster.jpg"
                    uid: "latest_entry"
    """

    @property
    def collection_validator(self) -> MultiUrlValidator:
        """Returns itself!"""
        return self

    def validate_with_variables(
        self, source_variables: List[str], override_variables: Dict[str, str]
    ) -> None:
        """
        Validates any source variables added by the collection
        """
        super().validate_with_variables(
            source_variables=source_variables, override_variables=override_variables
        )

        has_non_empty_url = False
        for url_validator in self.urls.list:
            has_non_empty_url |= bool(url_validator.url.apply_formatter(override_variables))

        if not has_non_empty_url:
            raise self._validation_exception("Must contain at least one url that is non-empty")


class MultiUrlDownloader(BaseUrlDownloader[MultiUrlDownloadOptions]):
    downloader_options_type = MultiUrlDownloadOptions
