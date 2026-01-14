import functools
from abc import ABC
from dataclasses import dataclass
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from ytdl_sub.script.functions import Functions
from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.array import UnresolvedArray
from ytdl_sub.script.types.resolvable import Argument
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import BuiltInFunctionType
from ytdl_sub.script.types.resolvable import FunctionType
from ytdl_sub.script.types.resolvable import FutureResolvable
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Lambda
from ytdl_sub.script.types.resolvable import NamedCustomFunction
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import ReturnableArgument
from ytdl_sub.script.types.resolvable import ReturnableArgumentA
from ytdl_sub.script.types.resolvable import ReturnableArgumentB
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency
from ytdl_sub.script.utils.exception_formatters import FunctionArgumentsExceptionFormatter
from ytdl_sub.script.utils.exceptions import UNREACHABLE
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException
from ytdl_sub.script.utils.exceptions import RuntimeException
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError
from ytdl_sub.script.utils.type_checking import FunctionSpec
from ytdl_sub.script.utils.type_checking import is_union


@dataclass(frozen=True)
class Function(FunctionType, VariableDependency, ABC):
    @property
    def iterable_arguments(self) -> List[Argument]:
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

            function_args: List[FunctionArgument] = []
            for i, arg in enumerate(resolved_args):
                function_arg = FunctionArgument.from_idx(idx=i, custom_function_name=self.name)

                if function_arg in resolved_variables:
                    # function args should always be unique since they are only defined once
                    # in the custom function as %custom_function_name___idx
                    # and returned as a set from each custom function.
                    raise UNREACHABLE

                resolved_variables[function_arg] = arg
                function_args.append(function_arg)

            out = custom_functions[self.name].resolve(
                resolved_variables=resolved_variables,
                custom_functions=custom_functions,
            )

            for function_arg in function_args:
                del resolved_variables[function_arg]

            return out

        # Implies the custom function does not exist. This should have
        # been checked in the parser with
        raise UNREACHABLE

    def partial_resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        unresolved_variables: Dict[Variable, Argument],
        custom_functions: Dict[str, VariableDependency],
    ) -> Argument | Resolvable:
        maybe_resolvable_args, _ = VariableDependency.try_partial_resolve(
            args=self.args,
            resolved_variables=resolved_variables,
            unresolved_variables=unresolved_variables,
            custom_functions=custom_functions,
        )

        for i in range(len(self.args)):
            function_arg = FunctionArgument.from_idx(idx=i, custom_function_name=self.name)
            function_value = maybe_resolvable_args[i]

            if isinstance(function_value, Resolvable):
                resolved_variables[function_arg] = function_value
            else:
                unresolved_variables[function_arg] = function_value

        assert len(custom_functions[self.name].iterable_arguments) == 1
        custom_function_definition = custom_functions[self.name].iterable_arguments[0]

        maybe_resolvable_custom_function, is_resolvable = VariableDependency.try_partial_resolve(
            args=[custom_function_definition],
            resolved_variables=resolved_variables,
            unresolved_variables=unresolved_variables,
            custom_functions=custom_functions,
        )

        for i in range(len(self.args)):
            function_arg = FunctionArgument.from_idx(idx=i, custom_function_name=self.name)

            if isinstance(maybe_resolvable_args[i], Resolvable):
                del resolved_variables[function_arg]
            else:
                del unresolved_variables[function_arg]

        if is_resolvable:
            return maybe_resolvable_custom_function[0]

        # Did not resolve custom function arguments, do not proceed
        return CustomFunction(name=self.name, args=maybe_resolvable_args)


class BuiltInFunction(Function, BuiltInFunctionType):
    def validate_args(self) -> "BuiltInFunction":
        """
        Ensures the args are compatible with the BuiltInFunction.
        """
        if not self.function_spec.is_compatible(input_args=self.args):
            raise FunctionArgumentsExceptionFormatter(
                input_spec=self.function_spec,
                function_instance=self,
            ).highlight()

        return self

    # pylint: disable=missing-raises-doc

    @property
    def callable(self) -> Callable[..., Resolvable]:
        """
        Returns
        -------
        The actual callable of the BuiltInFunction
        """
        try:
            return Functions.get(self.name)
        except Exception as exc:
            # Should be validated in the parser
            raise UNREACHABLE from exc

    # pylint: enable=missing-raises-doc

    @functools.cached_property
    def function_spec(self) -> FunctionSpec:
        """
        Returns
        -------
        The FunctionSpec of the BuiltInFunction
        """
        return FunctionSpec.from_callable(name=self.name, callable_ref=self.callable)

    @classmethod
    def _arg_output_type(cls, arg: Argument) -> Type[Argument]:
        if isinstance(arg, BuiltInFunction):
            return arg.output_type()
        if isinstance(arg, FutureResolvable):
            return arg.future_resolvable_type()
        return type(arg)

    @classmethod
    def _instantiate_lambda(cls, lambda_function_name: str, args: List[Argument]) -> Function:
        return (
            BuiltInFunction(name=lambda_function_name, args=args)
            if Functions.is_built_in(lambda_function_name)
            else CustomFunction(name=lambda_function_name, args=args)
        )

    def _output_type(self, union_args: List[Type[Argument]]) -> Type[Resolvable]:
        union_types_list = set()
        for union_type in union_args:
            possible_output_type = union_type
            if union_type in (ReturnableArgument, ReturnableArgumentA, ReturnableArgumentB):
                generic_arg_index = self.function_spec.args.index(union_type)
                possible_output_type = self._arg_output_type(self.args[generic_arg_index])

            if is_union(possible_output_type):
                union_types_list.update(possible_output_type.__args__)
            else:
                union_types_list.add(possible_output_type)

        return Union[tuple(union_types_list)]

    def output_type(self) -> Type[Resolvable]:
        """
        Returns
        -------
        The BuiltInFunction's true output type.
        """
        if is_union(self.function_spec.return_type):
            return self._output_type(self.function_spec.return_type.__args__)

        return self._output_type([self.function_spec.return_type])

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
        if not self.function_spec.is_lambda_function or len(function_input_lambda_args) != 1:
            raise UNREACHABLE

        lambda_function_name = function_input_lambda_args[0].value

        try:
            lambda_args = self.callable(*resolved_arguments)
        except Exception as exc:
            raise FunctionRuntimeException(
                f"Runtime error occurred when executing the function %{self.name}: {str(exc)}"
            ) from exc

        assert isinstance(lambda_args, Array)

        return self._resolve_argument_type(
            arg=UnresolvedArray(
                [
                    self._instantiate_lambda(
                        lambda_function_name=lambda_function_name, args=lambda_arg.value
                    )
                    for lambda_arg in lambda_args.value
                ]
            ),
            resolved_variables=resolved_variables,
            custom_functions=custom_functions,
        )

    def _resolve_lambda_reduce_function(
        self,
        resolved_arguments: List[Resolvable | Lambda],
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        """
        Resolve the lambda reduce function by
            1. Preemptively create the 'reduce-like' call-stack as unresolvable
            2. Resolve it like any other syntax
        """
        function_input_lambda_args = [arg for arg in resolved_arguments if isinstance(arg, Lambda)]
        if not self.function_spec.is_lambda_reduce_function or len(function_input_lambda_args) != 1:
            raise UNREACHABLE

        lambda_function_name = function_input_lambda_args[0].value

        try:
            lambda_array = self.callable(*resolved_arguments)
        except Exception as exc:
            raise FunctionRuntimeException(
                f"Runtime error occurred when executing the function %{self.name}: {str(exc)}"
            ) from exc

        assert isinstance(lambda_array, Array)

        if len(lambda_array.value) == 0:
            return Array(value=[])
        if len(lambda_array.value) == 1:
            return lambda_array.value[0]

        reduced: Resolvable = self._resolve_argument_type(
            arg=self._instantiate_lambda(
                lambda_function_name=lambda_function_name,
                args=[lambda_array.value[0], lambda_array.value[1]],
            ),
            resolved_variables=resolved_variables,
            custom_functions=custom_functions,
        )
        for idx in range(2, len(lambda_array.value)):
            reduced = self._resolve_argument_type(
                arg=self._instantiate_lambda(
                    lambda_function_name=lambda_function_name,
                    args=[reduced, lambda_array.value[idx]],
                ),
                resolved_variables=resolved_variables,
                custom_functions=custom_functions,
            )

        return reduced

    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        # Ensure conditionals do not execute all branches
        conditional_return_args = self.function_spec.conditional_arg_indices(
            num_input_args=len(self.args)
        )

        # Resolve all non-lambda arguments
        resolved_arguments: List[Resolvable | Lambda | ReturnableArgument] = [
            (
                self._resolve_argument_type(
                    arg=arg,
                    resolved_variables=resolved_variables,
                    custom_functions=custom_functions,
                )
                if idx not in conditional_return_args
                else ReturnableArgument(
                    value=functools.partial(
                        self._resolve_argument_type, arg, resolved_variables, custom_functions
                    )
                )
            )
            for idx, arg in enumerate(self.args)
        ]

        # If a lambda is in a function's arg, resolve it differently
        if self.function_spec.is_lambda_function:
            return self._resolve_lambda_function(
                resolved_arguments=resolved_arguments,
                resolved_variables=resolved_variables,
                custom_functions=custom_functions,
            )

        # If a lambda is in a function's arg, resolve it differently
        if self.function_spec.is_lambda_reduce_function:
            return self._resolve_lambda_reduce_function(
                resolved_arguments=resolved_arguments,
                resolved_variables=resolved_variables,
                custom_functions=custom_functions,
            )

        try:
            return self.callable(*resolved_arguments)
        except (UserThrownRuntimeError, RuntimeException):
            raise
        except Exception as exc:
            raise FunctionRuntimeException(
                f"Runtime error occurred when executing the function %{self.name}: {str(exc)}"
            ) from exc

    def _partial_resolve_conditional(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        unresolved_variables: Dict[Variable, Argument],
        custom_functions: Dict[str, "VariableDependency"],
    ):
        """
        If the conditional partially resolvable enough to warrant evaluation,
        perform it here.
        """
        if self.is_subset_of(
            variables=resolved_variables, custom_function_definitions=custom_functions
        ):
            return self.resolve(
                resolved_variables=resolved_variables,
                custom_functions=custom_functions,
            )

        if self.name == "if":
            maybe_resolvable_arg, is_resolvable = VariableDependency.try_partial_resolve(
                args=[self.args[0]],
                resolved_variables=resolved_variables,
                unresolved_variables=unresolved_variables,
                custom_functions=custom_functions,
            )
            if is_resolvable:
                boolean_output = maybe_resolvable_arg[0]
                assert isinstance(boolean_output, Boolean)
                return self.args[1] if boolean_output.native else self.args[2]

        if self.name == "elif":
            for idx in range(0, len(self.args), 2):
                maybe_resolvable_arg, is_resolvable = VariableDependency.try_partial_resolve(
                    args=[self.args[idx]],
                    resolved_variables=resolved_variables,
                    unresolved_variables=unresolved_variables,
                    custom_functions=custom_functions,
                )
                if is_resolvable:
                    boolean_output = maybe_resolvable_arg[0]
                    assert isinstance(boolean_output, Boolean)
                    if boolean_output.native:
                        return self.args[idx + 1]
                else:
                    break

        if self.name == "assert_then":
            maybe_resolvable_arg, is_resolvable = VariableDependency.try_partial_resolve(
                args=[self.args[0]],
                resolved_variables=resolved_variables,
                unresolved_variables=unresolved_variables,
                custom_functions=custom_functions,
            )
            if is_resolvable:
                boolean_output = maybe_resolvable_arg[0]
                assert isinstance(boolean_output, Boolean)
                if boolean_output.native:
                    return self.args[1]

        return self

    def _try_optimized_partial_resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        unresolved_variables: Dict[Variable, Argument],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Optional[Argument]:
        """
        If a function has enough (but not all) resolved parameters to warrant a return,
        perform it here.
        """
        if self.name == "array_at":
            if (
                isinstance(self.args[0], UnresolvedArray)
                and isinstance(self.args[1], Integer)
                and len(self.args[0].value) >= self.args[1].value
            ):
                maybe_resolvable_values, _ = VariableDependency.try_partial_resolve(
                    args=[self.args[0].value[self.args[1].value]],
                    resolved_variables=resolved_variables,
                    unresolved_variables=unresolved_variables,
                    custom_functions=custom_functions,
                )

                return maybe_resolvable_values[0]

        return None

    def partial_resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        unresolved_variables: Dict[Variable, Argument],
        custom_functions: Dict[str, VariableDependency],
    ) -> Argument | Resolvable:
        conditional_return_args = self.function_spec.conditional_arg_indices(
            num_input_args=len(self.args)
        )

        if conditional_return_args:
            return self._partial_resolve_conditional(
                resolved_variables=resolved_variables,
                unresolved_variables=unresolved_variables,
                custom_functions=custom_functions,
            )

        if partial_resolved := self._try_optimized_partial_resolve(
            resolved_variables=resolved_variables,
            unresolved_variables=unresolved_variables,
            custom_functions=custom_functions,
        ):
            return partial_resolved

        maybe_resolvable_values, is_resolvable = VariableDependency.try_partial_resolve(
            args=self.args,
            resolved_variables=resolved_variables,
            unresolved_variables=unresolved_variables,
            custom_functions=custom_functions,
        )

        out = BuiltInFunction(name=self.name, args=maybe_resolvable_values)
        if is_resolvable:
            return out.resolve(
                resolved_variables=resolved_variables,
                custom_functions=custom_functions,
            )

        return out

    def __hash__(self):
        return hash((self.name, *self.args))
