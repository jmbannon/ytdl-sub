import hashlib
import re
import shlex
from typing import Dict
from typing import List

from mergedeep import mergedeep

from ytdl_sub.config.config_file import ConfigOptions
from ytdl_sub.utils.exceptions import InvalidDlArguments


class DownloadArgsParser:
    """
    'Extra' arguments can be given to `ytdl-sub dl` which are meant to represent fields
    in a subscription yaml. This class will convert those extra args into a dict that can be
    passed in to instantiate a
    :class:`~ytdl_subscribe.validators.config.preset_validator.PresetValidator`
    """

    def __init__(self, extra_arguments: List[str], config_options: ConfigOptions):
        """
        Parameters
        ----------
        extra_arguments
          List of extra arguments from argparse
        config_options
          Configuration portion of config.yaml
        """
        self._unknown_arguments = extra_arguments
        self._config_options = config_options

    @property
    def _argument_exception(self) -> InvalidDlArguments:
        """
        :return: Exception to raise if a parsing error occurs.
        """
        return InvalidDlArguments(
            "dl arguments must be in the form of --subscription.option.name 'value'",
        )

    @classmethod
    def _is_argument_name(cls, arg: str) -> bool:
        """
        :param arg: Arg value from the unknown args list
        :return: True if it's an argument name, denoted by starting with '--'. False otherwise.
        """
        return arg.startswith("--")

    @classmethod
    def _get_argument_name(cls, arg_name: str) -> str:
        """
        Parameters
        ----------
        arg_name
            Argument name

        Returns
        -------
        The argument name with the -- removed
        """
        return arg_name[2:]

    @classmethod
    def _uses_list(cls, argument_name: str) -> bool:
        """
        :param argument_name: The argument name which might be using list
        :return: True if the argument uses list, denoted by ending with '[<positive integer>]'.
                 False otherwise.
        """
        pattern = re.compile(r"\[[1-9]\d*\]$")

        return bool(pattern.search(argument_name))

    @classmethod
    def _extract_list_index(cls, argument_name: str) -> int:
        """
        :param argument_name: The argument name using list
        :return: Splits the argument and returns the name and the list index.
        """
        prefix, _, last = argument_name.rpartition("[")

        return prefix, int(last[:-1]) - 1

    @classmethod
    def _find_largest_consecutive(cls, indices: List[int]) -> int:
        """
        :param indices: List of indices
        :return: Largest integer n + 1 so that all the integers from 0 up to n exist
                 in the indices.
                 -1 if indices list is empty or the smallest integer in indices is larger that 0.
        """
        largest_consecutive = -1
        indices.sort()

        for idx in indices:
            if idx - largest_consecutive <= 1:
                largest_consecutive = idx
            else:
                break

        return largest_consecutive + 1

    @classmethod
    def _argument_name_and_value_to_dict(cls, arg_name: str, arg_value: str) -> Dict:
        """
        :param arg_name: Argument name in the form of 'key1.key2.key3'
        :param arg_value: Argument value
        :return: dict containing {'key1':{'key2':{'key3': value}}}
        """
        argument_dict = {}

        # Remove the argument --'s, then split on period
        arg_name_split = cls._get_argument_name(arg_name).split(".")

        next_dict = argument_dict
        for next_arg_name in arg_name_split[:-1]:
            next_dict[next_arg_name] = {}
            next_dict = next_dict[next_arg_name]

        next_dict[arg_name_split[-1]] = arg_value

        return argument_dict

    @classmethod
    def _apply_aliases(cls, unknown_arguments: List[str], aliases: Dict) -> List[str]:
        """
        Applies any aliases from the config to the unknown arguments
        """
        applied_alias_arguments: List[str] = []

        for arg in unknown_arguments:
            if cls._is_argument_name(arg) and cls._get_argument_name(arg) in aliases:
                arg = aliases[cls._get_argument_name(arg)]
                applied_alias_arguments.extend(shlex.split(arg))
            else:
                applied_alias_arguments.append(arg)

        return applied_alias_arguments

    @classmethod
    def _make_lists(cls, arguments: List[str]) -> List[str]:
        """
        Assemble lists
        """
        list_arguments = {}
        new_arguments = []

        for idx in range(0, len(arguments), 2):
            argument_name, argument_value = arguments[idx], arguments[idx + 1]

            if not cls._uses_list(argument_name=argument_name):
                new_arguments.append(argument_name)
                new_arguments.append(argument_value)
                continue

            argument_name, list_index = cls._extract_list_index(argument_name=argument_name)

            if argument_name not in list_arguments:
                list_arguments[argument_name] = ([], [])

            list_arguments[argument_name][0].append(list_index)
            list_arguments[argument_name][1].append(argument_value)

        for name, (indices, values) in list_arguments.items():
            list_length = cls._find_largest_consecutive(indices=indices.copy())

            if list_length == 0:
                raise InvalidDlArguments("Incomplete list")

            list_value = [""] * list_length

            for idx, value in zip(indices, values):
                if idx < list_length:
                    list_value[idx] = value

            new_arguments.append(name)
            new_arguments.append(list_value)

        return new_arguments

    def to_subscription_dict(self) -> Dict:
        """
        Converts the extra arguments into a dict equivalent to a subscription yaml.
        :raises InvalidDlArguments: when an argument tries to use both list and non-list values.
        :return: dict containing argument names and values
        """
        arguments = self._apply_aliases(
            unknown_arguments=self._unknown_arguments, aliases=self._config_options.dl_aliases
        )
        if len(arguments) % 2 != 0:
            raise self._argument_exception

        if not all(
            (self._is_argument_name(arg=arguments[idx]) for idx in range(0, len(arguments), 2))
        ):
            raise self._argument_exception

        arguments = self._make_lists(arguments=arguments)
        subscription_dict = {}

        for idx in range(0, len(arguments), 2):
            argument_name, argument_value = arguments[idx], arguments[idx + 1]

            argument_dict = self._argument_name_and_value_to_dict(
                arg_name=argument_name, arg_value=argument_value
            )
            try:
                mergedeep.merge(
                    subscription_dict, argument_dict, strategy=mergedeep.Strategy.TYPESAFE_REPLACE
                )
            except TypeError as exc:
                raise InvalidDlArguments(
                    f"Invalid dl argument {argument_name}: "
                    "Cannot specify an argument to be two different types"
                ) from exc

        return subscription_dict

    def get_args_hash(self) -> str:
        """
        :return: Hash of the arguments provided
        """
        hash_string = str(sorted(self._unknown_arguments))
        return hashlib.sha256(hash_string.encode()).hexdigest()[-8:]
