from abc import ABC, abstractmethod
from typing import Tuple
import inspect

class SensorData:
    def __init__(self, x, y, t, sensor):
        self.x = x
        self.y = y
        self.t = t
        self.sensor = sensor

class UnitCore(ABC):
    @abstractmethod
    def update(self, sensor_data: SensorData) -> Tuple[float, float]:
        pass

    def __init_subclass__(cls):
        super().__init_subclass__()
        update_method = cls.__subclasses__()

        update_method = cls.__dict__.get('update')
        if update_method is None:
            raise NotImplementedError(f"{cls.__name__} must have update method.")
        
        sig = inspect.signature(update_method)
        params = list(sig.parameters.values())
        if len(params) != 2:
            raise TypeError(
                f"{cls.__name__}.update must have 2 arguments (self, sensor_data)."
            )
        if params[0].name != 'self':
            raise TypeError(
                f"The first argument of {cls.__name__}.update must be `self`."
            )