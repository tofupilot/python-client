from typing import Literal, cast

RunCreateFromFileBodyImporter = Literal["OPENHTF"]

RUN_CREATE_FROM_FILE_BODY_IMPORTER_VALUES: set[RunCreateFromFileBodyImporter] = {
    "OPENHTF",
}


def check_run_create_from_file_body_importer(value: str) -> RunCreateFromFileBodyImporter:
    if value in RUN_CREATE_FROM_FILE_BODY_IMPORTER_VALUES:
        return cast(RunCreateFromFileBodyImporter, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RUN_CREATE_FROM_FILE_BODY_IMPORTER_VALUES!r}")
