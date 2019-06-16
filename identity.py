from dataclasses import dataclass, field
from typing import Dict

from flask import current_app

from everyclass.rpc import ensure_slots
from everyclass.rpc.http import HttpRpc


def base_url():
    return current_app.config['IDENTITY_BASE_URL']


@dataclass
class GeneralResponse:
    success: bool
    err_code: field(default_factory=int)
    message: str

    @classmethod
    def make(cls, dct: Dict) -> "GeneralResponse":
        return cls(**ensure_slots(cls, dct))


class Login:
    @classmethod
    def login(cls, student_id: str, password: str):
        """登录

        4001 用户名为空
        4002 密码空
        4003 验证码验证未通过
        4004 学号不存在
        4005 此学生未注册
        4006 密码错误
        """
        if not student_id:
            ValueError("Empty Student ID")
        if not password:
            raise ValueError("Empty password")
        resp = HttpRpc.call(method='POST',
                            url='{}/login'.format(base_url()),
                            data={'student_id': student_id, 'password': password},
                            retry=True)
        return GeneralResponse.make(resp)


class Register:
    @classmethod
    def register(cls, student_id: str):
        """检查学号是否已注册

        4001 用户名为空
        4007 已经注册过了
        """
        resp = HttpRpc.call(method='POST',
                            url='{}/register'.format(base_url()),
                            data={'student_id': student_id},
                            retry=True)
        return GeneralResponse.make(resp)

    @classmethod
    def register_by_email(cls, student_id: str):
        """使用邮箱验证注册

        4001 用户名为空
        4007 已经注册过了
        5001 未定义的错误
        """
        resp = HttpRpc.call(method='POST',
                            url='{}/register/byEmail'.format(base_url()),
                            data={'student_id': student_id},
                            retry=True)
        return GeneralResponse.make(resp)
