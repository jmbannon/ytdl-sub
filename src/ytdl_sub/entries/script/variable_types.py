from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.map import Map
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String

ENTRY_METADATA_VARIABLE_NAME = "entry_metadata"
PLAYLIST_METADATA_VARIABLE_NAME = "playlist_metadata"
SOURCE_METADATA_VARIABLE_NAME = "source_metadata"

MetadataVariableT = TypeVar("MetadataVariableT", bound="MetadataVariable")
VariableT = TypeVar("VariableT", bound="Variable")


def _get(
    cast: str,
    metadata_variable_name: str,
    metadata_key: str,
    variable_name: Optional[str],
    default: Optional[VariableT | str | int | Dict | List],
    as_type: Type[MetadataVariableT],
) -> MetadataVariableT:
    if default is None:
        # TODO: assert with good error message if key DNE
        out = f"%map_get({metadata_variable_name}, '{metadata_key}')"
    elif isinstance(default, Variable):
        args = f"{metadata_variable_name}, '{metadata_key}', {default.variable_name}"
        out = f"%map_get_non_empty({args})"
    elif isinstance(default, str):
        out = f"%map_get_non_empty({metadata_variable_name}, '{metadata_key}', '{default}')"
    elif isinstance(default, dict):
        out = f"%map_get_non_empty({metadata_variable_name}, '{metadata_key}', {{}})"
    elif isinstance(default, list):
        out = f"%map_get_non_empty({metadata_variable_name}, '{metadata_key}', [])"
    else:
        out = f"%map_get_non_empty({metadata_variable_name}, '{metadata_key}', {default})"

    return as_type(
        variable_name=variable_name or metadata_key,
        metadata_key=metadata_key,
        definition=f"{{ %legacy_bracket_safety(%{cast}({out})) }}",
    )


@dataclass(frozen=True)
class Variable(ABC):
    variable_name: str
    definition: str

    @classmethod
    @abstractmethod
    def human_readable_type(cls) -> str:
        """
        Script type of the variable, for documentation
        """


@dataclass(frozen=True)
class BooleanVariable(Variable):
    @classmethod
    def human_readable_type(cls) -> str:
        return Boolean.__name__


@dataclass(frozen=True)
class StringVariable(Variable):
    @classmethod
    def human_readable_type(cls) -> str:
        return String.__name__

    def to_sanitized_plex(self, variable_name: str) -> "StringVariable":
        """
        Converts a String variable to be plex sanitized
        """
        return StringVariable(
            variable_name=variable_name,
            definition=f"{{%sanitize_plex_episode({self.variable_name})}}",
        )

    def as_date_variable(self) -> "StringDateVariable":
        """
        Converts a String variable to a date variable (which has metadata helpers)
        """
        return StringDateVariable(
            variable_name=self.variable_name,
            definition=self.definition,
        )


@dataclass(frozen=True)
class StringDateVariable(StringVariable):
    def get_string_date_metadata(
        self, date_metadata_key: str, variable_name: Optional[str] = None
    ) -> StringVariable:
        """
        Gets a string-based date metadata variable
        """
        return StringVariable(
            variable_name=variable_name or date_metadata_key,
            definition=f"""{{
                %string(
                    %map_get(
                      %to_date_metadata({self.variable_name}),
                      '{date_metadata_key}'
                    )
                )
            }}""",
        )

    def get_integer_date_metadata(
        self, date_metadata_key: str, variable_name: str
    ) -> "IntegerVariable":
        """
        Gets an int-based date metadata variable
        """
        return IntegerVariable(
            variable_name=variable_name,
            definition=f"""{{
                %int(
                    %map_get(
                      %to_date_metadata({self.variable_name}),
                      '{date_metadata_key}'
                    )
                )
            }}""",
        )


@dataclass(frozen=True)
class IntegerVariable(Variable):
    @classmethod
    def human_readable_type(cls) -> str:
        return Integer.__name__

    def to_padded_int(self, variable_name: str, pad: int) -> StringVariable:
        """
        Pads an integer
        """
        return StringVariable(
            variable_name=variable_name, definition=f"{{%pad_zero({self.variable_name}, {pad})}}"
        )


@dataclass(frozen=True)
class ArrayVariable(Variable):
    @classmethod
    def human_readable_type(cls) -> str:
        return Array.__name__


@dataclass(frozen=True)
class MapVariable(Variable):
    @classmethod
    def human_readable_type(cls) -> str:
        return Map.__name__


@dataclass(frozen=True)
class MetadataVariable(Variable, ABC):
    metadata_key: str


@dataclass(frozen=True)
class MapMetadataVariable(MetadataVariable, MapVariable):
    @classmethod
    def from_entry(
        cls,
        metadata_key: str,
        variable_name: Optional[str] = None,
        default: Optional["MapMetadataVariable" | Dict] = None,
    ) -> "MapMetadataVariable":
        """
        Creates a map variable from entry metadata
        """
        return _get(
            "map",
            metadata_variable_name=ENTRY_METADATA_VARIABLE_NAME,
            metadata_key=metadata_key,
            variable_name=variable_name,
            default=default,
            as_type=MapMetadataVariable,
        )


@dataclass(frozen=True)
class ArrayMetadataVariable(MetadataVariable, ArrayVariable):
    @classmethod
    def from_entry(
        cls,
        metadata_key: str,
        variable_name: Optional[str] = None,
        default: Optional["ArrayMetadataVariable" | List] = None,
    ) -> "ArrayMetadataVariable":
        """
        Creates an array variable from entry metadata
        """
        return _get(
            "array",
            metadata_variable_name=ENTRY_METADATA_VARIABLE_NAME,
            metadata_key=metadata_key,
            variable_name=variable_name,
            default=default,
            as_type=ArrayMetadataVariable,
        )


@dataclass(frozen=True)
class StringMetadataVariable(MetadataVariable, StringVariable):
    @classmethod
    def from_entry(
        cls,
        metadata_key: str,
        variable_name: Optional[str] = None,
        default: Optional[StringVariable | str] = None,
    ) -> "StringMetadataVariable":
        """
        Creates a string variable from entry metadata
        """
        return _get(
            "string",
            metadata_variable_name=ENTRY_METADATA_VARIABLE_NAME,
            metadata_key=metadata_key,
            variable_name=variable_name,
            default=default,
            as_type=StringMetadataVariable,
        )

    @classmethod
    def from_playlist(
        cls,
        metadata_key: str,
        variable_name: Optional[str] = None,
        default: Optional[StringVariable | str] = None,
    ) -> "StringMetadataVariable":
        """
        Creates a string variable from playlist metadata
        """
        return _get(
            "string",
            metadata_variable_name=PLAYLIST_METADATA_VARIABLE_NAME,
            metadata_key=metadata_key,
            variable_name=variable_name,
            default=default,
            as_type=StringMetadataVariable,
        )

    @classmethod
    def from_source(
        cls,
        metadata_key: str,
        variable_name: Optional[str] = None,
        default: Optional[StringVariable | str] = None,
    ) -> "StringMetadataVariable":
        """
        Creates a string variable from source metadata
        """
        return _get(
            "string",
            metadata_variable_name=SOURCE_METADATA_VARIABLE_NAME,
            metadata_key=metadata_key,
            variable_name=variable_name,
            default=default,
            as_type=StringMetadataVariable,
        )

    def as_date_variable(self) -> "StringDateMetadataVariable":
        """
        Converts a String variable to a date variable (which has metadata helpers)
        """
        return StringDateMetadataVariable(
            metadata_key=self.metadata_key,
            variable_name=self.variable_name,
            definition=self.definition,
        )


@dataclass(frozen=True)
class StringDateMetadataVariable(StringMetadataVariable, StringDateVariable):
    pass


@dataclass(frozen=True)
class IntegerMetadataVariable(MetadataVariable, IntegerVariable):
    @classmethod
    def from_entry(
        cls,
        metadata_key: str,
        variable_name: Optional[str] = None,
        default: Optional[IntegerVariable | int] = None,
    ) -> "IntegerMetadataVariable":
        """
        Creates an int variable from entry metadata
        """
        return _get(
            "int",
            metadata_variable_name=ENTRY_METADATA_VARIABLE_NAME,
            metadata_key=metadata_key,
            variable_name=variable_name,
            default=default,
            as_type=IntegerMetadataVariable,
        )

    @classmethod
    def from_playlist(
        cls,
        metadata_key: str,
        variable_name: Optional[str] = None,
        default: Optional[IntegerVariable | int] = None,
    ) -> "IntegerMetadataVariable":
        """
        Creates an int variable from playlist metadata
        """
        return _get(
            "int",
            metadata_variable_name=PLAYLIST_METADATA_VARIABLE_NAME,
            metadata_key=metadata_key,
            variable_name=variable_name,
            default=default,
            as_type=IntegerMetadataVariable,
        )
