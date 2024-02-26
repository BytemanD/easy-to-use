from dataclasses import dataclass
from dataclasses import field
from typing import List

import toml


class Choises:
    choises: list = None


@dataclass
class Option(Choises):
    name: str
    default: str = None
    value = None
    required: bool = False

    def __post_init__(self):
        if self.default is not None and not isinstance(self.default, str):
            raise ValueError(f'{self.default} is not string')

    def parse_value(self, value):
        return value

    def _valid(self, value):
        if self.choises and value not in self.choises:
            raise ValueError(f'"{value}" is invalid, must be {self.choises}')

    def set(self, value) -> None:
        val = self.parse_value(value)
        self._valid(val)
        self.value = val

    def get(self):
        return self.value if (self.value is not None) else self.default

    def dump(self):
        val = self.get()
        if self.required and val is None:
            return '<!required>'
        else:
            return val


@dataclass
class IntOption(Option, Choises):
    default: int = None
    min: int = None
    max: int = None

    def __post_init__(self):
        if self.default is not None and not isinstance(self.default, int):
            raise ValueError(f'{self.default} is not int or None')

    def parse_value(self, value):
        return int(value)

    def _valid(self, value: int) -> None:
        if self.min is not None and value < self.min:
            raise ValueError(f'"{value}" is invalid, must >= {self.min}')
        if self.max is not None and value > self.max:
            raise ValueError(f'"{value}" is invalid, must <= {self.max}')
        super()._valid(value)


@dataclass
class BoolOption(Option):
    default: bool = False

    def __post_init__(self):
        if not isinstance(self.default, bool):
            raise ValueError(f'{self.default} is not bool')

    def parse_value(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            upper_value = value.upper()
            if upper_value in ['TRUE', 'FALSE']:
                return upper_value == 'TRUE'
        raise ValueError(f'"{value}" is invalid, must be true or false')


@dataclass
class ListOption(Option):
    default: list = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.default, list):
            raise ValueError(f'{self.default} is not list')

    def parse_value(self, value):
        if isinstance(value, str):
            return [value]
        else:
            return list(value)


class OptionGroup(object):
    _NAME = ''
    _DESCIPTION = ''

    def __getattribute__(self, __name: str):
        attr = object.__getattribute__(self, __name)
        if isinstance(attr, Option):
            return attr.get()
        return object.__getattribute__(self, __name)

    def load_dict(self, data: dict):
        for name in dir(self):
            attr = object.__getattribute__(self, name)
            if not isinstance(attr, Option):
                continue
            if name in data:
                attr.set(data.get(name))
            if attr.required and attr.default is None \
               and attr.value is None:
                raise ValueError(f'{name} is required')

    def set(self, name: str, value):
        attr = object.__getattribute__(self, name)
        attr.set(value)

    def dump(self):
        data = {}
        for name in dir(self):
            attr = object.__getattribute__(self, name)
            if isinstance(attr, Option):
                data[name] = attr.dump()

        return data


class TomlConfig(object):

    def __getattribute__(self, __name: str):
        attr = object.__getattribute__(self, __name)
        if isinstance(attr, Option):
            return attr.get()
        return attr

    @classmethod
    def load(cls, file):
        data = toml.load(file)
        for k in dir(cls):
            attr = getattr(cls, k)
            if not isinstance(attr, (Option, OptionGroup)):
                continue
            if isinstance(attr, Option) and k in data:
                attr.set(data.get(k))
                continue
            if k in data:
                attr.load_dict(data.get(k, {}))

    def set(self, name: str, value):
        attr = object.__getattribute__(self, name)
        attr.set(value)

    @classmethod
    def dumps_dict(cls):
        data = {}
        for k in dir(cls):
            attribute = getattr(cls, k)
            if not isinstance(attribute, (Option, OptionGroup)):
                continue
            if isinstance(attribute, Option):
                data[k] = attribute.dump()
            else:
                data[k] = attribute.dump()
        return data


    @classmethod
    def dumps(cls, lines=True):
        return toml.dumps(cls.dumps_dict())
