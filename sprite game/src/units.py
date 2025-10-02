from src.settings import *

class Unit:
    def __init__(self, hp, damage, cost):
        self.hp = hp
        self.damage = damage
        self.cost = cost

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def is_dead(self):
        return self.hp <= 0

class Swordsman(Unit):
    def __init__(self):
        super().__init__(SWORDSMAN_HP, SWORDSMAN_DAMAGE, SWORDSMAN_COST)

class Archer(Unit):
    def __init__(self):
        super().__init__(ARCHER_HP, ARCHER_DAMAGE, ARCHER_COST)

class Catapult(Unit):
    def __init__(self):
        super().__init__(CATAPULT_HP, CATAPULT_DAMAGE, CATAPULT_COST)
