import copy
from typing import Dict
from typing import Optional

import mergedeep


class YTDLOptionsBuilder:
    """
    A class to track any modifications made to ytdl options
    """

    def __init__(self):
        self._ytdl_options: Dict = {}

    def add(
        self,
        *ytdl_option_dicts: Optional[Dict],
        before: bool = False,
        strategy: mergedeep.Strategy = mergedeep.Strategy.TYPESAFE_ADDITIVE
    ) -> "YTDLOptionsBuilder":
        """
        Parameters
        ----------
        *ytdl_option_dicts
            One or many ytdl_option dicts. Can also contain None's for convenience
        before
            Optional. Whether to add these dicts before or after the original
        strategy
            Optional. mergedeep strategy. Defaults to TYPESAFE_ADDITIVE

        Returns
        -------
        instance with the added ytdl_option dict(s)
        """
        non_empty = [ytdl_options for ytdl_options in ytdl_option_dicts if ytdl_options is not None]

        if before:
            non_empty.append(self.to_dict())
            self._ytdl_options = {}

        mergedeep.merge(self._ytdl_options, *non_empty, strategy=strategy)
        return self

    def clone(self) -> "YTDLOptionsBuilder":
        """
        Returns
        -------
        Deep-copied instance
        """
        return copy.deepcopy(self)

    def to_dict(self) -> Dict:
        """
        Returns
        -------
        Deep-copied dict of the current builder state
        """
        return copy.deepcopy(self._ytdl_options)
