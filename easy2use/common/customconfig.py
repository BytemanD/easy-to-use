import json
import dataclasses

from easy2use.common import exceptions

DEFAULT_GROUP = 'default'


class ValueNotInChoices(exceptions.BaseException):
    _msg = 'Invalid value {value}, which not in {choices}.'


@dataclasses.dataclass
class Item(object):
    name: str
    default: str = None
    description: str = None
    choices: list = dataclasses.field(default_factory=list)
    value = None
    type = str

    def __post_init__(self):
        if self.choices and self.default and self.default not in self.choices:
            raise ValueNotInChoices(value=self.default, choices=self.choices)
        self.default = self.type(self.default)
        self.value = self.default

    def set(self, value):
        if self.choices and (value not in self.choices):
            raise ValueNotInChoices(value=self.value, choices=self.choices)
        self.value = self.type(value)

    def reset(self):
        self.value = self.default


class IntItem(Item):
    type = int


class BoolItem(Item):
    type = bool


class JsonConfig(object):
    """
    >>> jc = JsonConfig()
    >>> jc.register_items([
    ...     Item('host', default='localhost'),
    ...     IntItem('port', default=80),
    ...     BoolItem('debug', default=True),
    ... ])
    >>> print(jc.dump())
    {
        "default": {
            "host": "localhost",
            "port": 80,
            "debug": true
        }
    }
    """

    def __init__(self):
        self._items = {}

    def register_items(self, items, group=DEFAULT_GROUP):
        self._items.setdefault(group, {})
        for item in items:
            self._items[group][item.name] = item

    def set(self, name, value, group=DEFAULT_GROUP):
        if group not in self._items:
            raise Exception('group %s not found' % group)
        if name not in self._items[group]:
            raise Exception('item %s is not found')
        self._items[group][name].value = value

    def to_dict(self):
        dict_items = {}
        for group, items in self._items.items():
            for name, item in items.items():
                dict_items.setdefault(group, {})
                dict_items[group][name] = item.value
        return dict_items

    def dump(self):
        return json.dumps(self.to_dict(), indent=4)

    def save(self, file_path):
        with open(file_path, 'w') as f:
            self._save(f)

    def load(self, file_path):
        with open(file_path) as f:
            self._load(f)

    def _load(self, of):
        self._data = json.load(of)

    def _save(self, of):
        json.dump(self.to_dict(), of, indent=4)


class YamlConfig(JsonConfig):

    def save(self, file_path):
        import yaml
        with open(file_path, 'w') as f:
            yaml.dump(self.to_dict(), stream=f)
