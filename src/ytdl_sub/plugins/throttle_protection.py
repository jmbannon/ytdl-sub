import random
import time
from typing import Optional, Dict

from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.preset_options import OptionsDictValidator
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.validators import FloatValidator
from ytdl_sub.validators.validators import ProbabilityValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

logger = Logger.get("throttle-protection")


class RandomizedRangeValidator(StrictDictValidator):
    """
    Validator to specify a float range between [min, max)
    """

    _required_keys = {"max"}
    _optional_keys = {"min"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self._max = self._validate_key(key="max", validator=FloatValidator).value
        self._min = self._validate_key_if_present(
            key="min", validator=FloatValidator, default=0.0
        ).value

        if self._max < self._min:
            raise self._validation_exception(
                f"max ({self._max}) must be greater than or equal to min ({self._min})"
            )

    @property
    def randomized_float(self) -> float:
        """
        Returns
        -------
        A random float within the range
        """
        return random.uniform(self._min, self._max)

    @property
    def randomized_int(self) -> int:
        """
        Returns
        -------
        A random integer within the range after casting the min + max to ints
        """
        return random.randrange(int(self._min), int(self._max))


class ThrottleProtectionOptions(OptionsDictValidator):
    """
    Provides options to make ytdl-sub look more 'human-like'. For range-based values,
    a random number will be chosen within the range to avoid sleeps looking scripted.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           sleep_per_download_s:
             min: 2
             max: 10
           sleep_per_subscription_s:
             min: 9
             max: 14
           max_downloads_per_subscription:
             min: 10
             max: 36
           subscription_download_probability: 1.0
    """

    _optional_keys = {
        "sleep_per_download_s",
        "sleep_per_subscription_s",
        "max_downloads_per_subscription",
        "subscription_download_probability",
    }

    def __init__(self, name, value):
        super().__init__(name, value)

        self._sleep_per_download_s = self._validate_key_if_present(
            key="sleep_per_download_s", validator=RandomizedRangeValidator
        )
        self._sleep_per_subscription_s = self._validate_key_if_present(
            key="sleep_per_subscription_s", validator=RandomizedRangeValidator
        )
        self._max_downloads_per_subscription = self._validate_key_if_present(
            key="max_downloads_per_subscription", validator=RandomizedRangeValidator
        )
        self._subscription_download_probability = self._validate_key_if_present(
            key="subscription_download_probability", validator=ProbabilityValidator
        )

    @property
    def sleep_per_download_s(self) -> Optional[RandomizedRangeValidator]:
        """
        Range in seconds to sleep between each download. Does not include time it takes for ytdl-sub
        to perform post-processing.
        """
        return self._sleep_per_download_s

    @property
    def sleep_per_subscription_s(self) -> Optional[RandomizedRangeValidator]:
        """
        Range in seconds to sleep between each subscription.
        """
        return self._sleep_per_subscription_s

    @property
    def max_downloads_per_subscription(self) -> Optional[RandomizedRangeValidator]:
        """
        Range of downloads to perform per subscription.
        """
        return self._sleep_per_subscription_s

    @property
    def subscription_download_probability(self) -> Optional[ProbabilityValidator]:
        """
        Probability to perform any downloads for each subscription. This is only recommended to
        set if you run ytdl-sub in a cron-job, that way you are statistically guaranteed over time
        to eventually download the subscription.
        """
        return self._subscription_download_probability


class ThrottleProtectionPlugin(Plugin[ThrottleProtectionOptions]):
    plugin_options_type = ThrottleProtectionOptions

    def __init__(
        self,
        options: ThrottleProtectionOptions,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(options, overrides, enhanced_download_archive)
        self._subscription_download_counter: int = 0
        self._subscription_max_downloads: Optional[int] = None

        # If subscriptions have a max download limit, set it here for the first subscription
        if self.plugin_options.max_downloads_per_subscription:
            self._subscription_max_downloads = (
                self.plugin_options.max_downloads_per_subscription.randomized_int
            )

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        ytdl options to enable/disable when downloading entries for this specific plugin
        """
        if self.plugin_options.subscription_download_probability:
            # assume proba is set to 1.0, random.random() will always be < 1, so do nothing
            if random.random() < self.plugin_options.subscription_download_probability.value:
                return None

            # otherwise, do not perform any downloads
            return {
                "max_downloads": 0
            }

        return None

    def modify_entry_metadata(self, entry: Entry) -> Optional[Entry]:
        if (
            self._subscription_max_downloads is not None
            and self._subscription_download_counter >= self._subscription_max_downloads
        ):
            if self._subscription_download_counter == self._subscription_max_downloads:
                logger.info("reached subscription max downloads of %d", self._subscription_max_downloads)
                self._subscription_download_counter += 1  # increment to only print once

            return None

        return entry

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        if self._subscription_download_counter == 0:
            logger.info("setting subscription max downloads to %d", self._subscription_max_downloads)

        # Increment the counter
        self._subscription_download_counter += 1

        if self.plugin_options.sleep_per_download_s:
            sleep_time = self.plugin_options.sleep_per_download_s.randomized_float
            logger.info("sleeping between downloads for %0.2f seconds", sleep_time)
            time.sleep(sleep_time)

        return None

    def post_process_subscription(self):
        # Reset counter to 0 for the next subscription
        self._subscription_download_counter = 0

        # If present, reset max downloads for the next subscription
        if self.plugin_options.max_downloads_per_subscription:
            self._subscription_max_downloads = (
                self.plugin_options.max_downloads_per_subscription.randomized_int
            )

        if self.plugin_options.sleep_per_subscription_s:
            sleep_time = self.plugin_options.sleep_per_subscription_s.randomized_float
            logger.info("sleeping between subscriptions for %0.2f seconds", sleep_time)
            time.sleep(sleep_time)
