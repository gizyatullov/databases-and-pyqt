from socket import socket
from socket import SOCK_STREAM, AF_INET
import dis

from common.errors import NotDetectedSocket, DetectedSocket, UsingProhibitedMethod


class BaseVerifierMeta(type):
    FORBIDDEN_CALLS = ('',)

    @staticmethod
    def check_socket_usage(obj: object, tcp=False) -> bool:
        if not tcp:
            return any(map(lambda item: isinstance(item, socket), obj.__dict__.values()))

        sock = None
        for item in obj.__dict__.values():
            if isinstance(item, socket):
                sock = item
                break

        if not sock:
            return False

        return all((sock.type == SOCK_STREAM, sock.family == AF_INET))

    @staticmethod
    def _raise_error(error) -> None:
        raise error

    def __init__(cls, cls_name: str, bases: tuple, cls_dict: dict):
        methods = []
        for atr in cls_dict.values():
            try:
                ret = dis.get_instructions(atr)
            except TypeError:
                pass
            else:
                [methods.append(item.argval) for item in ret
                 if item.opname == 'LOAD_GLOBAL' and item.argval not in methods]

        [cls._raise_error(UsingProhibitedMethod(command)) for command in cls.FORBIDDEN_CALLS if command in methods]

        super().__init__(cls_name, bases, cls_dict)

    def __call__(cls, *args, **kwargs):
        inst = super().__call__(*args, **kwargs)

        socket_tcp_usage = cls.check_socket_usage(inst, tcp=True)
        if not socket_tcp_usage:
            raise NotDetectedSocket

        return inst


class _ClientVerifierMeta(BaseVerifierMeta):
    FORBIDDEN_CALLS = ('accept', 'listen')

    def __new__(mcs, cls_name: str, bases: tuple, cls_dict: dict):
        new_class = super().__new__(mcs, cls_name, bases, cls_dict)
        socket_usage = mcs.check_socket_usage(new_class)
        if socket_usage:
            raise DetectedSocket
        return new_class


class ClientVerifier(metaclass=_ClientVerifierMeta):
    pass


class _ServerVerifierMeta(BaseVerifierMeta):
    FORBIDDEN_CALLS = ('connect',)


class ServerVerifier(metaclass=_ServerVerifierMeta):
    pass
