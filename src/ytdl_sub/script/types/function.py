import copy
import functools
import inspect
from abc import ABC
from dataclasses import dataclass
from inspect import FullArgSpec
from typing import Callable
from typing import Dict
from typing import List
from typing import Type
from typing import Union

from ytdl_sub.script.functions import Functions
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.array import UnresolvedArray
from ytdl_sub.script.types.resolvable import Argument
from ytdl_sub.script.types.resolvable import FunctionType
from ytdl_sub.script.types.resolvable import Lambda
from ytdl_sub.script.types.resolvable import NamedCustomFunction
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import ReturnableArgument
from ytdl_sub.script.types.resolvable import ReturnableArgumentA
from ytdl_sub.script.types.resolvable import ReturnableArgumentB
from ytdl_sub.script.types.resolvable import TypeHintedFunctionType
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency
from ytdl_sub.script.utils.exception_formatters import FunctionArgumentsExceptionFormatter
from ytdl_sub.script.utils.exceptions import UNREACHABLE
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError
from ytdl_sub.script.utils.type_checking import FunctionInputSpec
from ytdl_sub.script.utils.type_checking import is_union


@dataclass(frozen=True)
class Function(FunctionType, VariableDependency, ABC):
    @property
    def _iterable_arguments(self) -> List[Argument]:
        return self.args


class CustomFunction(Function, NamedCustomFunction):
    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        resolved_args: List[Resolvable] = [
            self._resolve_argument_type(
                arg=arg, resolved_variables=resolved_variables, custom_functions=custom_functions
            )
            for arg in self.args
        ]

        if self.name in custom_functions:
            if len(self.args) != len(custom_functions[self.name].function_arguments):
                # Should be validated in the Script
                raise UNREACHABLE

            resolved_variables_with_args = copy.deepcopy(resolved_variables)
            for i, arg in enumerate(resolved_args):
                function_arg = FunctionArgument.from_idx(idx=i, custom_function_name=self.name)

                if function_arg in resolved_variables_with_args:
                    # function args should always be unique since they are only defined once
                    # in the custom function as %custom_function_name___idx
                    # and returned as a set from each custom function.
                    raise UNREACHABLE

                resolved_variables_with_args[function_arg] = arg

            return custom_functions[self.name].resolve(
                resolved_variables=resolved_variables_with_args,
                custom_functions=custom_functions,
            )

        # Implies the custom function does not exist. This should have
        # been checked in the parser with
        raise UNREACHABLE


class BuiltInFunction(Function, TypeHintedFunctionType):
    def validate_args(self) -> "BuiltInFunction":
        if not self.input_spec.is_compatible(input_args=self.args):
            raise FunctionArgumentsExceptionFormatter(
                input_spec=self.input_spec,
                function_instance=self,
            ).highlight()

        return self

    @property
    def callable(self) -> Callable[..., Resolvable]:
        if hasattr(Functions, self.name):
            return getattr(Functions, self.name)
        if hasattr(Functions, self.name + "_"):
            return getattr(Functions, self.name + "_")

        # Should be validated in the parser
        raise UNREACHABLE

    @functools.cached_property
    def arg_spec(self) -> FullArgSpec:
        return inspect.getfullargspec(self.callable)

    @property
    def input_spec(self) -> FunctionInputSpec:
        if self.arg_spec.varargs:
            return FunctionInputSpec(varargs=self.arg_spec.annotations[self.arg_spec.varargs])

        return FunctionInputSpec(
            args=[self.arg_spec.annotations[arg_name] for arg_name in self.arg_spec.args]
        )

    @property
    def is_lambda_function(self) -> bool:
        return Lambda in (self.input_spec.args or [])

    @classmethod
    def _arg_output_type(cls, arg: Argument) -> Type[Argument]:
        if isinstance(arg, BuiltInFunction):
            return arg.output_type()
        return type(arg)

    def output_type(self) -> Type[Resolvable]:
        output_type = self.arg_spec.annotations["return"]
        if is_union(output_type):
            union_types_list = []
            for union_type in output_type.__args__:
                if union_type in (ReturnableArgument, ReturnableArgumentA, ReturnableArgumentB):
                    generic_arg_index = self.input_spec.args.index(union_type)
                    union_types_list.append(self._arg_output_type(self.args[generic_arg_index]))
                else:
                    union_types_list.append(union_type)

            return Union[tuple(union_types_list)]

        return output_type

    def _resolve_lambda_function(
        self,
        resolved_arguments: List[Resolvable | Lambda],
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        """
        Resolve the lambda function by
            1. Calling the actual built-in function, which actually forms the input args to the
               lambda. NOTE: the lambda argument MUST BE the last argument in the input spec
               and output a ResolvedArray, where each element is the input args to the lambda.
            2. Preemptively creating the lambda's unresolved output array using output args from (1)
            3. Resolve it like any other syntax
        """
        function_input_lambda_args = [arg for arg in resolved_arguments if isinstance(arg, Lambda)]
        if not self.is_lambda_function or len(function_input_lambda_args) != 1:
            raise UNREACHABLE

        lambda_function_name = function_input_lambda_args[0].value

        try:
            lambda_args = self.callable(*resolved_arguments)
        except Exception as exc:
            raise FunctionRuntimeException(
                f"Runtime error occurred when executing the function %{self.name}: {str(exc)}"
            ) from exc

        assert isinstance(lambda_args, ResolvedArray)

        return self._resolve_argument_type(
            arg=UnresolvedArray(
                [
                    BuiltInFunction(name=lambda_function_name, args=lambda_arg.value)
                    if Functions.is_built_in(lambda_function_name)
                    else CustomFunction(name=lambda_function_name, args=lambda_arg.value)
                    for lambda_arg in lambda_args.value
                ]
            ),
            resolved_variables=resolved_variables,
            custom_functions=custom_functions,
        )

    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        # Resolve all non-lambda arguments
        resolved_arguments: List[Resolvable | Lambda] = [
            self._resolve_argument_type(
                arg=arg,
                resolved_variables=resolved_variables,
                custom_functions=custom_functions,
            )
            for arg in self.args
        ]

        # If a lambda is in a function's arg, resolve it differently
        if self.is_lambda_function:
            return self._resolve_lambda_function(
                resolved_arguments=resolved_arguments,
                resolved_variables=resolved_variables,
                custom_functions=custom_functions,
            )

        try:
            return self.callable(*resolved_arguments)
        except UserThrownRuntimeError:
            raise
        except Exception as exc:
            raise FunctionRuntimeException(
                f"Runtime error occurred when executing the function %{self.name}: {str(exc)}"
            ) from exc
