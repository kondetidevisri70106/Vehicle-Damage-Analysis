class Accelerometer:
    def __init__(self, addr=0x68):    # MPU-6050 default
        self.addr = addr

    def read(self):
        # Replace with smbus2 read
        return {"x": 0.0, "y": 0.0, "z": 9.81}