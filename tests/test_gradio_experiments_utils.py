import math

try:
    from gradio_experiments.utils import parse_env
except ImportError:
    # Fallback import for runs where the current project is not installed in the venv
    from utils import parse_env

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
