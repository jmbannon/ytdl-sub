import random
import time
from abc import ABC
from typing import Dict
from typing import Optional
from typing import Type
from typing import TypeVar

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import ToggleableOptionsDictValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import FloatFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesFloatFormatterValidator
from ytdl_sub.validators.validators import ProbabilityValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

logger = Logger.get("throttle-protection")

FloatValidatorT = TypeVar("FloatValidatorT", bound=FloatFormatterValidator)


class _RandomizedRangeValidator(StrictDictValidator, ABC):
    """
    Base class for range validation, to support both entry and static overrides.
    """

    _float_validator: Type[FloatValidatorT]

    _required_keys = {"max"}
    _optional_keys = {"min"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self._max = self._validate_key(key="max", validator=self._float_validator)
        self._min = self._validate_key_if_present(
            key="min", validator=self._float_validator, default=0.0
        )

    def _randomized_float(self, overrides: Overrides, entry: Optional[Entry] = None) -> float:
        actualized_min = float(overrides.apply_formatter(self._min, entry=entry))
        actualized_max = float(overrides.apply_formatter(self._max, entry=entry))

        if actualized_min < 0:
            raise self._validation_exception(
                f"min must be greater than zero, received {actualized_min}"
            )
        if actualized_max < actualized_min:
            raise self._validation_exception(
                f"max ({actualized_max}) must be greater than or equal to min ({actualized_min})"
            )

        return random.uniform(actualized_min, actualized_max)

    def _randomized_int(self, overrides: Overrides, entry: Optional[Entry] = None) -> int:
        """
        Returns
        -------
        A random float within the range, then cast to an integer (floored)
        """
        return int(self._randomized_float(overrides, entry=entry))

    def _max_value(self, overrides: Overrides, entry: Optional[Entry] = None) -> float:
        """
        Returns
        -------
        Max possible value
        """
        actualized_max = float(overrides.apply_formatter(self._max, entry=entry))
        if actualized_max < 0:
            raise self._validation_exception(
                f"max must be greater than zero, received {actualized_max}"
            )
        return actualized_max


class RandomizedRangeValidator(_RandomizedRangeValidator):
    """
    Validator to specify a float range between [min, max) with both
    override and entry variable support.
    """

    _float_validator = FloatFormatterValidator

    def randomized_float(self, overrides: Overrides, entry: Entry) -> float:
        """
        Returns
        -------
        A random float within the range
        """
        return self._randomized_float(overrides=overrides, entry=entry)

    def randomized_int(self, overrides: Overrides, entry: Entry) -> int:
        """
        Returns
        -------
        A random float within the range, then cast to an integer (floored)
        """
        return self._randomized_int(overrides=overrides, entry=entry)

    def max_value(self, overrides: Overrides, entry: Entry) -> float:
        """
        Returns
        -------
        Max possible value
        """
        return self._max_value(overrides=overrides, entry=entry)


class RandomizedRangeOverridesValidator(_RandomizedRangeValidator):
    """
    Validator to specify a float range between [min, max) with
    static variable support.
    """

    _float_validator = OverridesFloatFormatterValidator

    def randomized_float(self, overrides: Overrides) -> float:
        """
        Returns
        -------
        A random float within the range
        """
        return self._randomized_float(overrides=overrides)

    def randomized_int(self, overrides: Overrides) -> int:
        """
        Returns
        -------
        A random float within the range, then cast to an integer (floored)
        """
        return self._randomized_int(overrides=overrides)

    def max_value(self, overrides: Overrides) -> float:
        """
        Returns
        -------
        Max possible value
        """
        return self._max_value(overrides=overrides)


class ThrottleProtectionOptions(ToggleableOptionsDictValidator):
    """
    Provides options to make ytdl-sub look more 'human-like' to protect from throttling. For
    range-based values, a random number will be chosen within the range to avoid sleeps looking
    scripted.

    Range min and max values support static override variables within their definitions.
    ``sleep_per_download_s`` supports both static and override variables.

    :Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           throttle_protection:
             sleep_per_request_s:
               min: 5.5
               max: 10.4
             sleep_per_download_s:
               min: 2.2
               max: 10.8
             sleep_per_subscription_s:
               min: 9.0
               max: 14.1
             max_downloads_per_subscription:
               min: 10
               max: 36
             subscription_download_probability: 1.0
    """

    _optional_keys = {
        "enable",
        "sleep_per_request_s",
        "sleep_per_download_s",
        "sleep_per_subscription_s",
        "max_downloads_per_subscription",
        "subscription_download_probability",
    }

    def __init__(self, name, value):
        super().__init__(name, value)

        self._sleep_per_request_s = self._validate_key_if_present(
            key="sleep_per_request_s", validator=RandomizedRangeOverridesValidator
        )
        self._sleep_per_download_s = self._validate_key_if_present(
            key="sleep_per_download_s", validator=RandomizedRangeValidator
        )
        self._sleep_per_subscription_s = self._validate_key_if_present(
            key="sleep_per_subscription_s", validator=RandomizedRangeOverridesValidator
        )
        self._max_downloads_per_subscription = self._validate_key_if_present(
            key="max_downloads_per_subscription", validator=RandomizedRangeOverridesValidator
        )
        self._subscription_download_probability = self._validate_key_if_present(
            key="subscription_download_probability", validator=ProbabilityValidator
        )

    @property
    def sleep_per_request_s(self) -> Optional[RandomizedRangeValidator]:
        """
        :expected type: Optional[Range]
        :description:
          Number in seconds to sleep between each request during metadata download. Note that
          metadata download refers to the initial info.json download, not the actual audio/video
          download for the entry. Also, yt-dlp only supports a single value at this time for this,
          so will always use the max value.
        """
        return self._sleep_per_request_s

    @property
    def sleep_per_download_s(self) -> Optional[RandomizedRangeValidator]:
        """
        :expected type: Optional[Range]
        :description:
          Number in seconds to sleep between each download. Does not include time it takes for
          ytdl-sub to perform post-processing.
        """
        return self._sleep_per_download_s

    @property
    def sleep_per_subscription_s(self) -> Optional[RandomizedRangeValidator]:
        """
        :expected type: Optional[Range]
        :description:
          Number in seconds to sleep between each subscription.
        """
        return self._sleep_per_subscription_s

    @property
    def max_downloads_per_subscription(self) -> Optional[RandomizedRangeValidator]:
        """
        :expected type: Optional[Range]
        :description:
          Number of downloads to perform per subscription.
        """
        return self._max_downloads_per_subscription

    @property
    def subscription_download_probability(self) -> Optional[ProbabilityValidator]:
        """
        :expected type: Optional[Float]
        :description:
          Probability to perform any downloads, recomputed for each subscription. This is only
          recommended to set if you run ytdl-sub in a cron-job, that way you are statistically
          guaranteed over time to eventually download the subscription.
        """
        return self._subscription_download_probability


class ThrottleProtectionPlugin(Plugin[ThrottleProtectionOptions]):
    plugin_options_type = ThrottleProtectionOptions

    @classmethod
    def perform_sleep(cls, sleep_time: float) -> None:
        """
        Wrapper to be able to mock
        """
        time.sleep(sleep_time)

    def __init__(
        self,
        options: ThrottleProtectionOptions,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(options, overrides, enhanced_download_archive)
        self._subscription_download_counter: int = 0
        self._subscription_max_downloads: Optional[int] = None

        # Compute this during post-processing using entry metadata.
        # Apply the sleep post-completion.
        self._entry_sleep_time: Optional[float] = None

        # If subscriptions have a max download limit, set it here for the first subscription
        if self.plugin_options.max_downloads_per_subscription:
            self._subscription_max_downloads = (
                self.plugin_options.max_downloads_per_subscription.randomized_int(
                    overrides=self.overrides
                )
            )

    def ytdl_options(self) -> Optional[Dict]:
        if self.plugin_options.sleep_per_request_s is not None:
            return {
                "sleep_interval_requests": self.plugin_options.sleep_per_request_s.max_value(
                    overrides=self.overrides
                )
            }
        return {}

    def initialize_subscription(self) -> bool:
        if self.plugin_options.subscription_download_probability:
            proba = self.plugin_options.subscription_download_probability.value
            # assume proba is set to 1.0, random.random() will always be < 1, can never reach this
            if random.random() > proba:
                logger.info(
                    "Subscription download probability of %0.2f missed",
                    proba,
                )
                return False
        return True

    def modify_entry_metadata(self, entry: Entry) -> Optional[Entry]:
        if (
            self._subscription_max_downloads is not None
            and self._subscription_download_counter >= self._subscription_max_downloads
        ):
            if self._subscription_download_counter == self._subscription_max_downloads:
                logger.info(
                    "Reached subscription max downloads of %d for throttle protection",
                    self._subscription_max_downloads,
                )
                self._subscription_download_counter += 1  # increment to only print once

            return None

        return entry

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        if (
            self._subscription_max_downloads is not None
            and self._subscription_download_counter == 0
        ):
            logger.info(
                "Setting subscription max downloads to %d", self._subscription_max_downloads
            )

        # Increment the counter
        self._subscription_download_counter += 1

        if self.plugin_options.sleep_per_download_s:
            self._entry_sleep_time = self.plugin_options.sleep_per_download_s.randomized_float(
                overrides=self.overrides, entry=entry
            )

        return None

    def post_completion_entry(self, file_metadata: FileMetadata) -> None:
        if self._entry_sleep_time:
            # pylint: disable=logging-fstring-interpolation)
            # needed to test logs in unit test
            logger.info(f"Sleeping between downloads for {self._entry_sleep_time:.2f} seconds")
            self.perform_sleep(self._entry_sleep_time)

    def post_process_subscription(self):
        # Reset counter to 0 for the next subscription
        self._subscription_download_counter = 0

        # If present, reset max downloads for the next subscription
        if self.plugin_options.max_downloads_per_subscription:
            self._subscription_max_downloads = (
                self.plugin_options.max_downloads_per_subscription.randomized_int(
                    overrides=self.overrides
                )
            )

        if self.plugin_options.sleep_per_subscription_s:
            sleep_time = self.plugin_options.sleep_per_subscription_s.randomized_float(
                overrides=self.overrides
            )
            logger.info("Sleeping between subscriptions for %0.2f seconds", sleep_time)
            self.perform_sleep(sleep_time)
