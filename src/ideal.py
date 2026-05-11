class Ideal(frozenset):
    def __new__(cls, iterable=()):
        return super().__new__(cls, iterable)

    def __repr__(self):
        if not self:
            return "ideal()"
        return "ideal(" + ", ".join(sorted(self)) + ")"