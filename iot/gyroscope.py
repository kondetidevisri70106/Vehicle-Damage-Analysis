class Gyroscope:
    def __init__(self, addr=0x68):
        self.addr = addr

    def read(self):
        return {"x": 0.0, "y": 0.0, "z": 0.0}