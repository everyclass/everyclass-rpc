from dataclasses import dataclass, field
from typing import Dict, List

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


@dataclass
class EmailSetPasswordResponse:
    success: bool
    err_code: field(default_factory=int)
    message: str
    student_id: field(default_factory=str)

    @classmethod
    def make(cls, dct: Dict) -> "EmailSetPasswordResponse":
        return cls(**ensure_slots(cls, dct))


@dataclass
class RegisterByPasswordResponse:
    success: bool
    err_code: field(default_factory=int)
    message: str
    request_id: field(default_factory=str)

    @classmethod
    def make(cls, dct: Dict) -> "RegisterByPasswordResponse":
        return cls(**ensure_slots(cls, dct))


@dataclass
class PasswordStrengthResponse:
    success: bool
    strong: bool
    score: str

    @classmethod
    def make(cls, dct: Dict) -> "PasswordStrengthResponse":
        return cls(**ensure_slots(cls, dct))


@dataclass
class Visitor:
    name: str
    student_id: str
    last_semester: str
    visit_time: str

    @classmethod
    def make(cls, dct: Dict) -> "Visitor":
        return cls(**ensure_slots(cls, dct))


@dataclass
class VisitorsResponse:
    success: bool
    count: int
    visitors: List[Visitor]

    @classmethod
    def make(cls, dct: Dict) -> "VisitorsResponse":
        dct['visitors'] = [Visitor.make(x) for x in dct['visitors']]
        return cls(**ensure_slots(cls, dct))


# err_code 除了以下每个注释里写的之外还包括 408，500，400

class Login:
    @classmethod
    def login(cls, student_id: str, password: str, captcha_ticket: str, captcha_rand: str, remote_addr: str):
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
        resp = HttpRpc.call(method='GET',
                            url=f'{base_url()}/login',
                            data={'student_id'    : student_id,
                                  'password'      : password,
                                  'captcha_ticket': captcha_ticket,
                                  'captcha_rand'  : captcha_rand,
                                  'remote_addr'   : remote_addr},
                            retry=True)
        return GeneralResponse.make(resp)


class Register:
    @classmethod
    def register(cls, student_id: str):
        """检查学号是否已注册

        4001 用户名为空
        4007 已经注册过了
        """
        if not student_id:
            raise ValueError("Empty student ID")

        resp = HttpRpc.call(method='GET',
                            url=f'{base_url()}/register',
                            data={'student_id': student_id},
                            retry=True)
        return GeneralResponse.make(resp)

    @classmethod
    def register_by_email(cls, student_id: str):
        """使用邮箱验证注册

        4001 用户名为空
        4007 已经注册过了
        4501 未定义的错误
        """
        if not student_id:
            raise ValueError("Empty student ID")

        resp = HttpRpc.call(method='POST',
                            url=f'{base_url()}/register/byEmail',
                            data={'student_id': student_id},
                            retry=True)
        return GeneralResponse.make(resp)

    @classmethod
    def verify_email_token(cls, token: str):
        """验证邮箱 token

        4008 token 为空
        4009 token 无效
        """
        if not token:
            raise ValueError("Empty token")

        resp = HttpRpc.call(method='GET',
                            url=f'{base_url()}/register/emailVerification',
                            data={'token': token},
                            retry=True)
        return GeneralResponse.make(resp)

    @classmethod
    def email_set_password(cls, token: str, password: str):
        """邮件验证 设置密码

        4008 token 为空
        4002 密码为空
        4009 token 无效
        4010 密码强度太低
        """
        if not token:
            raise ValueError("Empty token")
        if not password:
            raise ValueError("Empty password")

        resp = HttpRpc.call(method='POST',
                            url=f'{base_url()}/register/emailVerification',
                            data={'token'   : token,
                                  'password': password},
                            retry=True)
        return EmailSetPasswordResponse.make(resp)

    @classmethod
    def register_by_password(cls, student_id: str, password: str, jw_password: str, captcha_ticket: str,
                             captcha_rand: str, remote_addr: str):
        """使用密码注册

        4001 学号为空
        4002 密码为空
        4010 密码太弱
        4003 验证码无效
        4501 everyclass-auth 服务错误
        """
        if not student_id:
            raise ValueError("Empty student ID")
        if not password:
            raise ValueError("Empty password")
        if not jw_password:
            raise ValueError("Empty JW password")

        resp = HttpRpc.call(method='POST',
                            url=f'{base_url()}/register/byPassword',
                            data={'student_id'    : student_id,
                                  'password'      : password,
                                  'jw_password'   : jw_password,
                                  'captcha_ticket': captcha_ticket,
                                  'captcha_rand'  : captcha_rand,
                                  'remote_addr'   : remote_addr},
                            retry=True)
        return RegisterByPasswordResponse.make(resp)

    @classmethod
    def check_password_strength(cls, password: str):
        """检查密码强度"""
        if not password:
            raise ValueError("Empty password")

        resp = HttpRpc.call(method='GET',
                            url=f'{base_url()}/register/passwordStrengthCheck',
                            data={'password': password},
                            retry=True)
        return PasswordStrengthResponse.make(resp)

    @classmethod
    def password_verification_status(cls, request_id: str):
        """检查密码验证的状态

        4011 请求 ID 为空
        4100 无效的请求 ID
        4007 已经注册过了
        4200 验证成功
        4201 下次查询
        4202 密码错误
        """
        if not request_id:
            raise ValueError("Empty request ID")

        resp = HttpRpc.call(method='GET',
                            url=f'{base_url()}/register/byPassword/statusRefresh',
                            data={'request_id': request_id},
                            retry=True)
        return GeneralResponse.make(resp)


class UserCentre:
    @classmethod
    def set_privacy_level(cls, student_id: str, privacy_level: int):
        """设置隐私级别

        4101 无效的隐私级别
        4100 无效的请求
        """
        if not student_id:
            raise ValueError("Empty student ID")
        if privacy_level is None:  # avoid 0
            raise ValueError("Empty privacy level")

        resp = HttpRpc.call(method='POST',
                            url=f'{base_url()}/setPreference',
                            data={'privacy_level': privacy_level},
                            headers={'STUDENT_ID': student_id},
                            retry=True)
        return GeneralResponse.make(resp)

    @classmethod
    def reset_calendar_token(cls, student_id: str):
        """清空日历 token
        """
        if not student_id:
            raise ValueError("Empty student ID")

        resp = HttpRpc.call(method='POST',
                            url=f'{base_url()}/resetCalendarToken',
                            headers={'STUDENT_ID': student_id},
                            retry=True)
        return GeneralResponse.make(resp)

    @classmethod
    def get_visitors(cls, student_id: str):
        """获得访客列表
        """
        if not student_id:
            raise ValueError("Empty student ID")

        resp = HttpRpc.call(method='GET',
                            url=f'{base_url()}/visitors',
                            headers={'STUDENT_ID': student_id},
                            retry=True)
        return VisitorsResponse.make(resp)
