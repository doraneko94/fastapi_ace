from abc import ABC, abstractmethod
from typing import final, Type
import sys

def __a():
    return

class Env:
    def __init__(self):
        pass

class UnitCore(ABC):
    def __init__(self, env: Env):
        self.env = env
        self.__x = 0.0
        self.__y = 0.0

    @classmethod
    def update(self) -> tuple[float, float]:
        pass

    @final
    def __process(self) -> None:
        self.update()

class RestrictedModule:
    def __init__(self):
        self._UnitCore = UnitCore
        self.__all__ = ["UnitCore"]

    def __getattr__(self, name):
        if name == "UnitCore":
            return self._UnitCore
        raise AttributeError(f"Module `{__name__}` has no attribute `{name}`")
    
    def __dir__(self):
        return ["UnitCore"]

sys.modules[__name__] = RestrictedModule()