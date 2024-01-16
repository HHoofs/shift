from dataclasses import dataclass


@dataclass
class A:
    a = [1, 2, 3, 4, 5]
    b = ["a", "b", "c", "d", "e"]

    def __iter__(self):
        yield from self.a
        yield from self.b

    def max(self):
        for i in self:
            print(i)


a = A()

a.max()


from enum import IntEnum


class Season(IntEnum):
    SPRING = 1
    SUMMER = 2
    AUTUMN = 3
    WINTER = 4


s = Season.SPRING
a = Season.AUTUMN

min([s, a])
