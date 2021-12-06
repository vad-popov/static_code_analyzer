class PiggyBank:
    # create __init__ and add_money methods
    def __init__(self, dollars, cents):
        self.dollars = dollars + cents // 100
        self.cents = cents % 100

    def add_money(self, deposit_dollars, deposit_cents):
        self.cents += deposit_cents
        self.dollars += deposit_dollars + self.cents // 100
        self.cents = self.cents % 100

    def __str__(self):
        return f'PigyBank Dollars: {self.dollars} Cents: {self.cents}'

pb = PiggyBank(1, 1)
pb.add_money(500, 500)
print(pb.dollars, pb.cents)
print(pb)