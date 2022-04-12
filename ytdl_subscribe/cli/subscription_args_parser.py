from typing import List


class SubscriptionArgsParser:
    """
    'Unknown' arguments can be given to `ytdl-sub dl` which are meant to represent fields
    in a subscription yaml. This class will convert those extra args into a
    :class:`~ytdl_subscribe.validators.config.preset_validator.PresetValidator`
    """

    def __init__(self, unknown_arguments: List[str]):
        self._unknown_arguments = unknown_arguments
