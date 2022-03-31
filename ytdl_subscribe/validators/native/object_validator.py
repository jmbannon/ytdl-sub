from typing import Set

from ytdl_subscribe.validators.native.validator import Validator


class ObjectValidator(Validator):

    required_fields: Set[str] = []
    optional_fields: Set[str] = []
    allow_extra_fields = False

    @property
    def allowed_fields(self):
        return sorted(self.required_fields.union(self.optional_fields))

    @property
    def object_keys(self):
        return sorted(list(self.value.keys()))

    @property
    def object_items(self):
        return self.value.items()

    def validate(self) -> "ObjectValidator":
        super().validate()

        # Ensure the value is an object
        if not isinstance(self.value, dict):
            error_msg = f"'{self.key}' must be an object"
            if self.required_fields:
                error_msg = f"{error_msg} with the required field: {', '.join(self.required_fields)}"
            raise ValueError(error_msg)

        # Ensure the object contains all the required fields
        for required_key in self.required_fields:
            if required_key not in self.value:
                error_msg = (
                    f"'{self.key}' is missing the required field '{required_key}'"
                )
                raise ValueError(error_msg)

        # If extra fields are not allowed, ensure we only have required or optional keys
        if not self.allow_extra_fields:
            for object_key in self.object_keys:
                if (
                    object_key not in self.required_fields
                    or object_key not in self.optional_fields
                ):

                    error_msg = (
                        f"'{self.key}' contains the field '{object_key} which is not allowed. "
                        f"Allowed fields: {', '.join(self.allowed_fields)}"
                    )
                    raise ValueError(error_msg)

        return self
