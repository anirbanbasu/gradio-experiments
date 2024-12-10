from gradio_experiments_utils.utils import Constants


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
