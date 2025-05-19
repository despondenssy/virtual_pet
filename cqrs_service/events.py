class EnergyChargedEvent:
    def __init__(self, pet_id: int, amount: int):
        self.pet_id = pet_id
        self.amount = amount

class EnergySpentEvent:
    def __init__(self, pet_id: int, amount: int):
        self.pet_id = pet_id
        self.amount = amount