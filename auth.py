# flake8: noqa
from dataclasses import dataclass, field
from typing import Dict

from everyclass.rpc import ensure_slots
from everyclass.rpc.http import HttpRpc

BASE_URL = 'everyclass-auth'


def set_base_url(base_url: str) -> None:
    global BASE_URL
    BASE_URL = base_url


@dataclass
class VerifyEmailTokenResult:
    success: bool
    request_id: field(default_factory=str)

    @classmethod
    def make(cls, dct: Dict) -> "VerifyEmailTokenResult":
        return cls(**ensure_slots(cls, dct))


@dataclass
class GetResultResult:
    success: bool
    message: str

    @classmethod
    def make(cls, dct: Dict) -> "GetResultResult":
        return cls(**ensure_slots(cls, dct))


class Auth:
    @classmethod
    def register_by_email(cls, request_id: str, student_id: str):
        return HttpRpc.call(method='POST',
                            url=f'{BASE_URL}/register_by_email',
                            data={'request_id': request_id,
                                  'student_id': student_id},
                            retry=True)

    @classmethod
    def verify_email_token(cls, token: str):
        resp = HttpRpc.call(method='POST',
                            url=f'{BASE_URL}/verify_email_token',
                            data={"email_token": token},
                            retry=True)
        return VerifyEmailTokenResult.make(resp)

    @classmethod
    def register_by_password(cls, request_id: str, student_id: str, password: str):
        return HttpRpc.call(method='POST',
                            url=f'{BASE_URL}/register_by_password',
                            data={'request_id': request_id,
                                  'student_id': student_id,
                                  'password'  : password})

    @classmethod
    def get_result(cls, request_id: str):
        resp = HttpRpc.call(method='GET',
                            url=f'{BASE_URL}/get_result',
                            data={'request_id': request_id},
                            retry=True)
        return GetResultResult.make(resp)
