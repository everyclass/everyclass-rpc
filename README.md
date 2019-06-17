# everyclass.rpc

每课后端微服务远程过程调用 SDK。提供微服务之间的通信功能，使得微服务之间的远程过程调用就像调用本地的函数一样。

## 使用示例
```python
def demo():
    from everyclass.rpc.auth import Auth
    try:
        result = Auth.get_result("123456")
    except Exception as e:
        return handle_exception(e)
    
    if not result.success:
        if result.err_code == 3401:
            pass # handle exception based on specific error code
        elif result.err_code == 3402:
            pass # handle another exception based on specific error code
    else:
        pass # do something
```

当 HTTP 状态码为 4XX 或 5XX 时，本 SDK 会抛出异常。调用方需要通过 `try...except` 语句来处理异常。因为具体的场景不同，调用不同的服务时可能需要编写不同的 `handle_exception` 函数。

除此之外，即便 HTTP 的状态码为 200，也可能有业务上的错误需要处理。可以通过返回值中的 `success` 属性来判断是否出错，并通过 `err_code` 和 `message` 来判断错误的具体内容以便进行处理。具体的错误码应该在注释和文档中注明。

## 业务错误码约定
鉴于 HTTP 使用三位数作为状态码，为了便于与 HTTP 状态码进行区分，我们约定使用四位数作为业务上的状态码，其中：
- 第一位为服务的编号（约定 server 为 1，entity 为 2，auth 为 3，identity 为 4）
- 后三位为自编的错误码，约定 4 开头为用户操作异常，5 开头为服务器内部异常

示例：4401 代表 everyclass-identity 服务由于用户的错误请求产生的一个异常，它的具体含义可以在 ``everyclass.rpc.consts.identity`` 中找到。