class Transaction:
    def __init__(self, transaction_id, user_id, amount, time, time_readable, merchant,location):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.amount = amount
        self.time = time
        self.time_readable = time_readable
        self.merchant = merchant
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