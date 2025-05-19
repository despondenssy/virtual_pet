class ChargeEnergyCommand:
    def __init__(self, pet_id: int, amount: int):
        self.pet_id = pet_id
        self.amount = amount

class SpendEnergyCommand:
    def __init__(self, pet_id: int, amount: int):
        self.pet_id = pet_id
        self.amount = amount