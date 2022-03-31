from typing import List


class SubscriptionSourceName(object):
    YOUTUBE = "youtube"
    SOUNDCLOUD = "soundcloud"

    @classmethod
    def all(cls) -> List[str]:
        """Returns all Subscription sources sorted as a list"""
        return sorted([cls.YOUTUBE, cls.SOUNDCLOUD])

    @classmethod
    def pretty_all(cls) -> str:
        """Returns all subscription sources pretty printed"""
        return ", ".join(cls.all())
