import hashlib
import re
import shlex
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from mergedeep import mergedeep

from ytdl_sub.cli.parsers.main import MainArguments
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.config_validator import ConfigOptions
from ytdl_sub.utils.exceptions import InvalidDlArguments


class DownloadArgsParser:
    """
    'Extra' arguments can be given to `ytdl-sub dl` which are meant to represent fields
    in a subscription yaml. This class will convert those extra args into a dict that can be
    passed in to instantiate a
    :class:`~ytdl_subscribe.validators.config.preset_validator.PresetValidator`
    """

    # pattern to search for the [...] part in the argument name
    _list_index_pattern = re.compile(r"\[([1-9]\d*)\]$")

    def __init__(self, extra_arguments: List[str], config_options: ConfigOptions):
        """
        Parameters
        ----------
        extra_arguments
          List of extra arguments from argparse
        config_options
          Configuration portion of config.yaml

        Raises
        ------
        InvalidDlArguments
            If extra arguments contains a ytdl-sub arg
        """
        self._unknown_arguments = extra_arguments
        self._config_options = config_options

        for arg in extra_arguments:
            if arg in MainArguments.all_arguments():
                raise InvalidDlArguments(
                    f"'{arg}' is a ytdl-sub argument and must placed behind 'dl'"
                )

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
    def _get_list_index_if_exists(cls, argument_name: str) -> Tuple[str, int]:
        """
        :param argument_name: Argument name
        :return: Argument name and -1 if argument name does not use list.
                 Argument name and list index (a non-negative integer) otherwise.

        Examples
        --------
            _get_list_index_if_exists("--key1.key2") -> ("--key1.key2", -1)
            _get_list_index_if_exists("--key1.key2[5]") -> ("--key1.key2", 5)
        """
        search = cls._list_index_pattern.search(argument_name)

        if search is None:
            return argument_name, -1

        return argument_name[: search.start()], int(search.group(1)) - 1

    @classmethod
    def _find_largest_consecutive(cls, indices: List[int]) -> int:
        """
        :param indices: List of indices
        :return: Largest integer n + 1 so that all the integers from 0 up to n exist
                 in the indices.
                 0 if indices list is empty or the smallest integer in indices is larger than 0.
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
    def _argument_name_and_value_to_dict(cls, arg_name: str, arg_value: Any) -> Dict:
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

        if isinstance(arg_value, str):
            if arg_value == "True":
                next_dict[arg_name_split[-1]] = True
            elif arg_value == "False":
                next_dict[arg_name_split[-1]] = False
            elif arg_value.isdigit():
                next_dict[arg_name_split[-1]] = int(arg_value)
            elif arg_value.replace(".", "", 1).isdigit():
                next_dict[arg_name_split[-1]] = float(arg_value)

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
            argument_name, list_index = cls._get_list_index_if_exists(argument_name=argument_name)

            if list_index == -1:
                new_arguments.append(argument_name)
                new_arguments.append(argument_value)
                continue

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

    @classmethod
    def from_dl_override(cls, override: str, config: ConfigFile) -> "DownloadArgsParser":
        """
        Create a DownloadArgsParser from a sub --override argument value
        """
        return DownloadArgsParser(
            extra_arguments=override.split(), config_options=config.config_options
        )
