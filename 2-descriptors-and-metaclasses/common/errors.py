"""Кастомные исключения"""


class NotDict(Exception):
    def __init__(self, txt=''):
        self.txt = txt


class NotBytes(Exception):
    def __init__(self, txt=''):
        self.txt = txt


class MaxLen(Exception):
    def __init__(self, txt=''):
        self.txt = txt


class NotDetectedSocket(Exception):
    pass


class DetectedSocket(Exception):
    pass


class UsingProhibitedMethod(Exception):
    pass


class NoFunctionCall(Exception):
    pass
