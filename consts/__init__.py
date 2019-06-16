from typing import NamedTuple


class Error(NamedTuple):
    err_code: int
    message: str
