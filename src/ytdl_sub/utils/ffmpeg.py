import subprocess

from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.logger import Logger

logger = Logger.get(name="ffmpeg")


class FFMPEG:
    @classmethod
    def _ensure_installed(cls):
        try:
            subprocess.check_output(["which", "ffmpeg"])
        except subprocess.CalledProcessError as subprocess_error:
            raise ValidationException(
                "Trying to use a feature which requires ffmpeg, but it cannot be found"
            ) from subprocess_error

    @classmethod
    def run(cls, ffmpeg_args: str) -> None:
        """
        Runs an ffmpeg command. Should not include 'ffmpeg' as the beginning argument.

        Parameters
        ----------
        ffmpeg_args:
            Arguments to pass to ffmpeg. Each one will be separated by a space.
        """
        cls._ensure_installed()

        cmd = f"ffmpeg {ffmpeg_args}"
        logger.debug("Running %s", cmd)
        subprocess.run(cmd, check=True)
