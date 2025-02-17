from core import SensorData, UnitCore

a = 0

class FighterA(UnitCore):
    def __init__(self):
        self.a = a
        pass

    def update(self, sensor_data: SensorData):
        return (1, 0)
    
class FighterB(UnitCore):
    def __init__(self):
        pass

    def update(self, sensor_data: SensorData):
        return (0.7, 0)
    
fa = FighterA()
print(fa.update(0))
print("Hello")