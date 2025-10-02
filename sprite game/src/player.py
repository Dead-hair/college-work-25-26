class Player:
    def __init__(self, gold=200):
        self.gold = gold
        self.units = []

    def buy_unit(self, unit_class):
        unit = unit_class()
        if self.gold >= unit.cost:
            self.gold -= unit.cost
            self.units.append(unit)
            return True
        else:
            return False

    def get_units(self):
        return self.units
