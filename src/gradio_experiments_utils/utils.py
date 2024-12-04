# gradio-experiments: A collection of feature experiments with Gradio
# Copyright (C) 2024 Anirban Basu

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from typing import Any


class Constants:
    """A class to hold constants used in the library. This class can be subclassed to add more constants."""

    SPACE_STRING = " "
    """The space character."""

    TRUE_VALUES_LIST = ["true", "yes", "t", "y", "on"]
    """A list of string values that are considered as True."""

    EMPTY_LIST = []
    """An empty list."""

    EMPTY_DICT = {}
    """An empty dictionary."""


def parse_env(
    var_name: str,
    default_value: str | None = None,
    type_cast=str,
    convert_to_list=False,
    list_split_char=Constants.SPACE_STRING,
) -> Any | list[Any]:
    """
    Parse an environment variable and return the value.

    Args:
        var_name (str): The name of the environment variable.
        default_value (str | None): The default value to use if the environment variable is not set. Defaults to None.
        type_cast (str): The type to cast the value to.
        convert_to_list (bool): Whether to convert the value to a list.
        list_split_char (str): The character to split the list on.

    Returns:
        (Any | list[Any]) The parsed value, either as a single value or a list. The type of the returned single
        value or individual elements in the list depends on the supplied type_cast parameter.
    """
    if os.getenv(var_name) is None and default_value is None:
        raise ValueError(
            f"Environment variable {var_name} does not exist and a default value has not been provided."
        )
    parsed_value = None
    if type_cast is bool:
        parsed_value = (
            os.getenv(var_name, default_value).lower() in Constants.TRUE_VALUES_LIST
        )
    else:
        parsed_value = os.getenv(var_name, default_value)

    value: Any | list[Any] = (
        type_cast(parsed_value)
        if not convert_to_list
        else [type_cast(v) for v in parsed_value.split(list_split_char)]
    )
    return value
