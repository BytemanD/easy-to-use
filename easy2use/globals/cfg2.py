from dataclasses import dataclass


@dataclass
class Option:
    name: str
    default: str = None
    value = None
    choises: list = None
    required: bool = False

    def parse_value(self, value):
        return value

    def set(self, value) -> None:
        val = self.parse_value(value)
        if self.choises and val not in self.choises:
            raise ValueError(f'"{val}" is not valid, must be {self.choises}')
        self.value = val

    def get(self):
        return self.value if (self.value is not None) else self.default


class IntOption(Option):
    default: str = None

    def parse_value(self, value):
        return int(value)


class BoolOption(Option):
    default: bool = False

    def parse_value(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            upper_value = value.upper()
            if upper_value in ['TRUE', 'FALSE']:
                return upper_value == 'TRUE'
        raise ValueError(f'"{value}" is not valid, must be true or false')


class ListOption(Option):
    default: str = []

    def parse_value(self, value):
        return list(value)


class OptionGroup(object):

    def __getattribute__(self, __name: str):
        attr = object.__getattribute__(self, __name)
        if isinstance(attr, Option):
            return attr.get()
        return object.__getattribute__(self, __name)

    def load_dict(self, data: dict):
        for name in dir(self):
            option = object.__getattribute__(self, name)
            if not isinstance(option, Option):
                continue
            if name in data:
                option.set(data.get(name))

            if option.required and option.default is None \
               and option.value is None:
                raise ValueError(f'{name} is required')
