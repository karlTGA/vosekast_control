class Tank:

    def __init__(self, name, capacity, level_sensor, drain_sensor, overflow_sensor):
        self.name = name
        self.capacity = capacity
        self.level_sensor = level_sensor
        self.drain_sensor = drain_sensor
        self.overflow_sensor = overflow_sensor
