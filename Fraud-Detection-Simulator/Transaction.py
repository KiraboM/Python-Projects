class Transaction:
    def __init__(self, id, name, amount, time, location):
        self.id = id
        self.name = name
        self.amount = amount
        self.time = time
        self.location = location

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_amount(self):
        return self.amount

    def set_amount(self, amount):
        self.amount = amount

    def get_time(self):
        return self.time

    def set_time(self, time):
        self.time = time

    def get_location(self):
        return self.location

    def set_location(self, location):
        self.location = location