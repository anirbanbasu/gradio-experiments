import os
from typing import Any

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


class Constants:
    """A class to hold constants used in the library. This class can be subclassed to add more constants."""

    EMPTY_STRING = ""
    """An empty string."""

    SPACE_STRING = " "
    """The space character."""

    COMMA = ","
    """The comma character."""

    TRUE_VALUES_LIST = ["true", "yes", "t", "y", "on"]
    """A list of string values that are considered as True."""

    EMPTY_LIST = []
    """An empty list."""

    EMPTY_DICT = {}
    """An empty dictionary."""

    CRLF = "\r\n"
    """The carriage return and line feed characters."""

    LF = "\n"
    """The line feed character."""


def parse_env(
    var_name: str,
    default_value: Any | None = None,
    allowed_values: list[Any] | None = None,
    type_cast: type = str,
    convert_to_list=False,
    list_split_char=Constants.SPACE_STRING,
) -> Any | list[Any]:
    """
    Parse the environment variable and return the value.

    Args:
        var_name (str): The name of the environment variable.
        default_value (Any | None): The default value to use if the environment variable is not set. Defaults to None.
        allowed_values (list[Any] | None): A list of allowed values for the environment variable. If provided, the
            value will be checked against this list. This option is ignored if type_cast is bool.
        type_cast (type): The type to cast the value to.
        convert_to_list (bool): Whether to convert the value to a list.
        list_split_char (str): The character to split the list on.

    Returns:
        (Any | list[Any]) The parsed value, either as a single value or a list. The type of the returned single
        value or individual elements in the list depends on the supplied type_cast parameter.
    """
    if default_value is not None and not isinstance(default_value, type_cast):
        raise TypeError(
            f"The default value {default_value} specified for the environment variable {var_name} is of type {type(default_value).__name__}. However, the expected type is {type_cast.__name__} instead."
        )
    if os.getenv(var_name) is None and default_value is None:
        raise ValueError(
            f"Environment variable {var_name} does not exist and a default value has not been provided."
        )
    parsed_value = None
    if type_cast is bool:
        # Sometimes, the environment variable is set to a string that represents a boolean value.
        # We convert it to lowercase and check against TRUE_VALUES_LIST.
        # The following logic also works if the boolean value is set to a True or False boolean type.
        parsed_value = (
            str(os.getenv(var_name, default_value)).lower()
            in Constants.TRUE_VALUES_LIST
        )
    else:
        parsed_value = os.getenv(var_name, default_value)
        if allowed_values is not None:
            if parsed_value not in allowed_values:
                raise ValueError(
                    f"Environment variable {var_name} has value '{parsed_value}', "
                    f"which is not in the allowed values: {allowed_values}."
                )

    if not convert_to_list:
        value: Any = (
            type_cast(parsed_value)
            if not isinstance(parsed_value, type_cast)
            else parsed_value
        )
    else:
        value: list[Any] = [
            (type_cast(v) if not isinstance(v, type_cast) else v)
            for v in parsed_value.split(list_split_char)
        ]
    return value


class AppConstants(Constants):
    FILE_EXTENSION_CSV = ".csv"
    FILE_EXTENSION_JSON = ".json"
    FILE_EXTENSION_PARQUET = ".parquet"
    ALLOWED_DATASET_FILE_EXTENSIONS = [
        FILE_EXTENSION_CSV,
        FILE_EXTENSION_JSON,
        FILE_EXTENSION_PARQUET,
    ]


class EnvironmentVariables:
    LOCAL_STORAGE_ENCRYPTION_KEY = "LOCAL_STORAGE_ENCRYPTION_KEY"
