class Base:
    def __init__(self, hp):
        self.hp = hp

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def is_destroyed(self):
        return self.hp <= 0
