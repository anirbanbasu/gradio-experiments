from uuid import uuid4

from environs import Env

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


env = Env()
ic(env.read_env())


class Constants:
    """A class to hold constants used in the library. This class can be subclassed to add more constants."""

    EMPTY_STRING = ""
    """An empty string."""

    SPACE_STRING = " "
    """The space character."""

    COMMA = ","
    """The comma character."""

    CRLF = "\r\n"
    """The carriage return and line feed characters."""

    LF = "\n"
    """The line feed character."""


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
    LOCAL_STORAGE_ENCRYPTION_KEY = env.str(
        "LOCAL_STORAGE_ENCRYPTION_KEY", default=uuid4().hex
    )
