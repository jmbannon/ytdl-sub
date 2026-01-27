import json
import re
from typing import Any
from typing import Dict
from typing import Optional

from ytdl_sub.script.parser import parse
from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.array import UnresolvedArray
from ytdl_sub.script.types.function import BuiltInFunction
from ytdl_sub.script.types.function import Function
from ytdl_sub.script.types.map import Map
from ytdl_sub.script.types.map import UnresolvedMap
from ytdl_sub.script.types.resolvable import Argument
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Lambda
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import UNREACHABLE
from ytdl_sub.script.utils.name_validation import is_function

# pylint: disable=too-many-return-statements


class ScriptUtils:
    @classmethod
    def add_sanitized_variables(cls, variables: Dict[str, str]) -> Dict[str, str]:
        """
        Helper to add sanitized variables to a Script
        """
        sanitized_variables = {
            f"{name}_sanitized": f"{{%sanitize({name})}}"
            for name in variables.keys()
            if not is_function(name)
        }
        return dict(variables, **sanitized_variables)

    @classmethod
    def add_sanitized_parsed_variables(
        cls, variables: Dict[str, SyntaxTree]
    ) -> Dict[str, SyntaxTree]:
        """
        Helper to add sanitized variables to a Script
        """
        sanitized_variables = {
            f"{name}_sanitized": SyntaxTree(
                ast=[BuiltInFunction(name="sanitize", args=[Variable(name)])]
            )
            for name in variables.keys()
            if not is_function(name)
        }
        return variables | sanitized_variables

    @classmethod
    def to_script(cls, value: Any, sort_keys: bool = True) -> str:
        """
        Converts a python value to a script value
        """
        if value is None:
            out = ""
        elif isinstance(value, str):
            out = value
        elif isinstance(value, bool):
            out = f"{{%bool({value})}}"
        elif isinstance(value, int):
            out = f"{{%int({value})}}"
        elif isinstance(value, float):
            out = f"{{%float({value})}}"
        else:
            dumped_json = json.dumps(value, ensure_ascii=False, sort_keys=sort_keys)
            # Remove triple-single-quotes from JSON to avoid parsing issues
            dumped_json = re.sub("'{3,}", "'", dumped_json)

            out = f"{{%from_json('''{dumped_json}''')}}"

        return out

    @classmethod
    def _to_script_argument(cls, value: Any) -> Argument:
        # Handle simple types as above
        if value is None or (isinstance(value, str) and value == ""):
            return String("")
        if isinstance(value, str):
            ast = parse(text=value).ast
            if len(ast) == 1:
                return ast[0]

            return BuiltInFunction(name="concat", args=ast)
        if isinstance(value, bool):
            return Boolean(value)
        if isinstance(value, int):
            return Integer(value)
        if isinstance(value, float):
            return Float(value)
        if isinstance(value, list):
            return UnresolvedArray([cls._to_script_argument(val) for val in value])
        if isinstance(value, dict):
            return UnresolvedMap(
                {
                    cls._to_script_argument(key): cls._to_script_argument(val)
                    for key, val in value.items()
                }
            )

        raise UNREACHABLE

    @classmethod
    def _get_quote_char(cls, arg: str) -> str:
        contains_single_quote = "'" in arg
        contains_double_quote = '"' in arg

        if not contains_single_quote and not contains_double_quote:
            return '"'
        if not contains_single_quote and contains_double_quote:
            return "'"
        if contains_single_quote and not contains_double_quote:
            return '"'
        return "'''"

    @classmethod
    def _to_script_code(cls, arg: Argument, top_level: bool = False) -> str:
        if not top_level and isinstance(arg, (Integer, Boolean, Float)):
            return str(arg.native)

        if isinstance(arg, String):
            if arg.native == "":
                return "" if top_level else "''"

            quote = cls._get_quote_char(arg.native)

            return arg.native if top_level else f"{quote}{arg.native}{quote}"

        if isinstance(arg, Integer):
            out = f"%int({arg.native})"
        elif isinstance(arg, Boolean):
            out = f"%bool({arg.native})"
        elif isinstance(arg, Float):
            out = f"%float({arg.native})"
        elif isinstance(arg, (Array, UnresolvedArray)):
            out = f"[ {', '.join(cls._to_script_code(val) for val in arg.value)} ]"
        elif isinstance(arg, (Map, UnresolvedMap)):
            kv_list = (
                f"{cls._to_script_code(key)}: {cls._to_script_code(val)}"
                for key, val in arg.value.items()
            )
            out = f"{{ {', '.join(kv_list)} }}"
        elif isinstance(arg, Variable):
            out = arg.name
        elif isinstance(arg, Function):
            out = f"%{arg.name}( {', '.join(cls._to_script_code(val) for val in arg.args)} )"
        elif isinstance(arg, Lambda):
            out = f"%{arg.value}"
        else:
            raise UNREACHABLE
        return f"{{ {out} }}" if top_level else out

    @classmethod
    def _is_top_level_string(cls, tree: SyntaxTree) -> Optional[str]:
        if not (
            len(tree.ast) == 1
            and isinstance(tree.ast[0], BuiltInFunction)
            and tree.ast[0].name == "concat"
        ):
            return None

        output = ""
        for arg in tree.ast[0].args:
            if isinstance(arg, BuiltInFunction) and arg.name == "string" and len(arg.args) == 1:
                output += cls._to_script_code(arg.args[0], top_level=True)
            else:
                output += cls._to_script_code(arg, top_level=True)

        return output

    @classmethod
    def _syntax_tree_to_native_script(cls, tree: SyntaxTree) -> str:

        if (output := cls._is_top_level_string(tree)) is not None:
            return output

        output = ""
        for arg in tree.ast:
            output += cls._to_script_code(arg, top_level=True)
        return output

    @classmethod
    def to_native_script(cls, value: Any) -> str:
        """
        Converts any JSON-compatible value into equivalent script syntax
        """
        if isinstance(value, SyntaxTree):
            return cls._syntax_tree_to_native_script(value)

        return cls._to_script_code(cls._to_script_argument(value), top_level=True)

    @classmethod
    def bool_formatter_output(cls, output: str) -> bool:
        """
        Translate formatter output to a boolean
        """
        if not output or output.lower() == "false":
            return False
        try:
            return bool(json.loads(output))
        except Exception:  # pylint: disable=broad-except
            return True
