"""
状态码分为两种，三位数的是 HTTP 状态码，四位数的是业务状态码。业务状态码的第一位代表服务名，约定 server、entity、auth、identity
分别为 1、2、3、4。

RPC 调用时如果遇到不可恢复的错误，如调用超时（HTTP 408），则抛出错误。对于业务代码的错误，不抛出错误，而交返回结果由业务自行处理。

"""
import os
from dataclasses import fields
from typing import Dict, Optional, Tuple

from flask import current_app, jsonify

_logger = None
_sentry = None
_resource_id_encrypt = None


def init(logger=None, sentry=None, resource_id_encrypt_function=None):
    """初始化 everyclass.rpc 模块

    """
    global _logger, _sentry, _resource_id_encrypt

    if logger:
        _logger = logger
    if sentry:
        _sentry = sentry
    if resource_id_encrypt_function:
        _resource_id_encrypt = resource_id_encrypt_function


def plugin_available(plugin_name: str) -> bool:
    """
    check if a plugin (Sentry, apm, logstash) is available in the current environment.
    :return True if available else False
    """
    mode = os.environ.get("MODE", None)
    if mode:
        return mode.lower() in current_app.config[f"{plugin_name.upper()}_AVAILABLE_IN"]
    else:
        raise EnvironmentError("MODE not in environment variables")


def _return_string(status_code, string, sentry_capture=False, log=None):
    if sentry_capture and plugin_available("sentry"):
        _sentry.captureException()
    if log:
        _logger.info(log)
    return string, status_code


def _return_json(status_code: int, json, sentry_capture=False, log=None):
    if sentry_capture and plugin_available("sentry") and _sentry:
        _sentry.captureException()
    if log and _logger:
        _logger.info(log)
    resp = jsonify(json)
    resp.status_code = status_code
    return resp


def handle_exception_with_message(e: Exception) -> Tuple:
    """
    处理调用上游服务时的错误，返回错误消息文本"""
    if isinstance(e, RpcTimeout):
        return _return_string(408, "Backend timeout", sentry_capture=True)
    elif isinstance(e, RpcResourceNotFound):
        return _return_string(404, "Resource not found", sentry_capture=True)
    elif isinstance(e, RpcBadRequest):
        return _return_string(400, "Bad request", sentry_capture=True)
    elif isinstance(e, RpcClientException):
        return _return_string(400, "Bad request", sentry_capture=True)
    elif isinstance(e, RpcServerException):
        return _return_string(500, "Server internal error", sentry_capture=True)
    else:
        return _return_string(500, "Server internal error", sentry_capture=True)


def handle_exception_with_json(e: Exception, lazy=False) -> Optional[Tuple]:
    """
    处理调用上游服务时的错误，返回 JSON Response （调用方直接返回）或 None（交给调用方自己处理错误）

    Usage:

    ```
    try:
        result = SomeRPC.call()
    except Exception as e:
        ret = handle_exception_with_json(e)
        if ret:
            return ret  # return if there is un-recoverable failure
        else:
            pass  # handle business exception
    ```

    ```
    try:
        result = SomeRPC.call()
    except Exception as e:
        return handle_exception_with_json(e)  # not recommended. only for legacy systems.
    ```

    :param e: 错误
    :param lazy: 如果为 true，代替业务方处理客户端错误以减少样板代码
    :return:
    """
    if isinstance(e, RpcTimeout):
        return _return_json(408, {"success" : False,
                                  "err_code": 408,
                                  "message" : f"Backend timeout. Root cause: {repr(e)}"})
    elif isinstance(e, RpcServerException):
        return _return_json(500, {"success" : False,
                                  "err_code": 500,
                                  "message" : f"Server internal error. Root cause: {repr(e)}"})
    if lazy:
        return _return_json(400, {"success" : False,
                                  "err_code": 400,
                                  "message" : f"Bad request. Root cause: {repr(e)}"})
    else:
        return None


def ensure_slots(cls, dct: Dict):
    """移除 dataclass 中不存在的key，预防 dataclass 的 __init__ 中 unexpected argument 的发生。"""
    _names = [x.name for x in fields(cls)]
    _del = []
    for key in dct:
        if key not in _names:
            _del.append(key)
    for key in _del:
        del dct[key]  # delete unexpected keys
        from everyclass.rpc import _logger
        _logger.warn(
            "Unexpected field `{}` is removed when converting dict to dataclass `{}`".format(key, cls.__name__))
    return dct


class RpcException(ConnectionError):
    """HTTP 4xx or 5xx"""
    pass


class RpcTimeout(RpcException, TimeoutError):
    """timeout"""
    pass


class RpcClientException(RpcException):
    """HTTP 4xx"""
    pass


class RpcResourceNotFound(RpcClientException):
    """HTTP 404"""
    pass


class RpcBadRequest(RpcClientException):
    """HTTP 400"""
    pass


class RpcServerException(RpcException):
    """HTTP 5xx"""
    pass


class RpcServerNotAvailable(RpcServerException):
    """HTTP 503"""
    pass
