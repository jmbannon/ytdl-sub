from ytdl_subscribe.validators.validators import LiteralDictValidator


class YTDLOptionsValidator(LiteralDictValidator):
    """Ensures `ytdl_options` is a dict"""
