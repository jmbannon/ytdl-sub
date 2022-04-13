import hashlib
from argparse import ArgumentError
from typing import Dict
from typing import List

from mergedeep import mergedeep


class DownloadArgsParser:
    """
    'Extra' arguments can be given to `ytdl-sub dl` which are meant to represent fields
    in a subscription yaml. This class will convert those extra args into a dict that can be
    passed in to instantiate a
    :class:`~ytdl_subscribe.validators.config.preset_validator.PresetValidator`
    """

    def __init__(self, extra_arguments: List[str]):
        """
        :param extra_arguments: List of extra arguments from argparse
        """
        self._unknown_arguments = extra_arguments

    @property
    def _argument_exception(self) -> ArgumentError:
        """
        :return: Exception to raise if a parsing error occurs.
        """
        return ArgumentError(
            argument=None,
            message="dl arguments must be in the form of --subscription.option.name 'value' "
            "proceeding the url",
        )

    @classmethod
    def _is_argument_name(cls, arg: str) -> bool:
        """
        :param arg: Arg value from the unknown args list
        :return: True if it's an argument name, denoted by starting with '--'. False otherwise.
        """
        return arg.startswith("--")

    @classmethod
    def _argument_name_and_value_to_dict(cls, arg_name: str, arg_value: str) -> Dict:
        """
        :param arg_name: Argument name in the form of 'key1.key2.key3'
        :param arg_value: Argument value
        :return: dict containing {'key1':{'key2':{'key3': value}}}
        """
        argument_dict = {}

        # Remove the argument --'s, then split on period
        arg_name_split = arg_name.replace("--", "", 1).split(".")

        next_dict = argument_dict
        for next_arg_name in arg_name_split[:-1]:
            next_dict[next_arg_name] = {}
            next_dict = next_dict[next_arg_name]

        next_dict[arg_name_split[-1]] = arg_value

        return argument_dict

    def to_subscription_dict(self) -> Dict:
        """
        Converts the extra arguments into a dict equivalent to a subscription yaml.
        :return: dict containing argument names and values
        """
        subscription_dict = {}
        if len(self._unknown_arguments) % 2 != 0:
            raise self._argument_exception

        for idx in range(0, len(self._unknown_arguments), 2):
            argument_name = self._unknown_arguments[idx]
            argument_value = self._unknown_arguments[idx + 1]

            if not self._is_argument_name(arg=argument_name):
                raise self._argument_exception

            argument_dict = self._argument_name_and_value_to_dict(
                arg_name=argument_name, arg_value=argument_value
            )
            mergedeep.merge(subscription_dict, argument_dict, strategy=mergedeep.Strategy.REPLACE)

        return subscription_dict

    def get_args_hash(self) -> str:
        """
        :return: Hash of the arguments provided
        """
        hash_string = str(sorted(self._unknown_arguments))
        return hashlib.sha256(hash_string.encode()).hexdigest()[-8:]
