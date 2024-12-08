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

import math
from gradio_experiments_utils.utils import parse_env
from uuid import uuid4


def test_parse_env():
    assert parse_env(f"RANDOM_KEY_{uuid4()}", default_value="UNKNOWN") == "UNKNOWN"
    assert parse_env(
        f"RANDOM_KEY_{uuid4()}", default_value="a b c d", convert_to_list=True
    ) == [
        "a",
        "b",
        "c",
        "d",
    ]
    assert parse_env(
        f"RANDOM_KEY_{uuid4()}",
        default_value="1 2 3 4",
        type_cast=int,
        convert_to_list=True,
    ) == [1, 2, 3, 4]
    assert (
        parse_env(f"RANDOM_KEY_{uuid4()}", default_value="on", type_cast=bool) is True
    )
    assert (
        parse_env(f"RANDOM_KEY_{uuid4()}", default_value="1234.5678", type_cast=float)
        == 1234.5678
    )
    assert (
        math.isclose(
            parse_env(f"RANDOM_KEY_{uuid4()}", default_value="3.14", type_cast=float),
            math.pi,
            rel_tol=1e-2,
        )
        is True
    )
    # This could fail if the user renames the working directory.
    assert str(parse_env("PWD")).endswith("gradio-experiments") is True
