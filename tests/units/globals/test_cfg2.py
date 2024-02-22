from easy2use.globals import cfg2
import unittest
from unittest import mock


def get_option_group() -> cfg2.OptionGroup:

    class OptionGroupDemo(cfg2.OptionGroup):
        id = cfg2.Option('id', required=True)
        name = cfg2.Option('name', default='foo')
        age = cfg2.IntOption('age', default=0)
        sex = cfg2.Option('sex')
        alive = cfg2.BoolOption('alive', default=True)

    return OptionGroupDemo()


def get_option_group_without_required() -> cfg2.OptionGroup:

    class OptionGroupDemo(cfg2.OptionGroup):
        name = cfg2.Option('name', default='foo')
        age = cfg2.IntOption('age', default=0)
        sex = cfg2.Option('sex')
        alive = cfg2.BoolOption('alive', default=True)

    return OptionGroupDemo()


def get_toml_config() -> cfg2.TomlConfig:

    class TomlConfigDemo(cfg2.TomlConfig):
        debug = cfg2.BoolOption('debug', default=False)
        log_file = cfg2.Option('log_file')
        list_option = cfg2.ListOption('list_option')
        people = get_option_group()
        people2 = get_option_group_without_required()

    return TomlConfigDemo()


class OptionGroupTestCases(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.group = get_option_group()

    def test_raise_required(self):
        self.assertRaises(ValueError, self.group.load_dict, {})

    def test_default(self):
        self.group.load_dict({'id': '1'})
        self.assertEqual(self.group.name, 'foo')
        self.assertEqual(self.group.age, 0)
        self.assertEqual(self.group.sex, None)
        self.assertEqual(self.group.alive, True)

    def test_not_default(self):
        self.group.load_dict({'id': '1', 'name': 'bar', 'sex': 'male',
                              'alive': False})
        self.assertEqual(self.group.name, 'bar')
        self.assertEqual(self.group.age, 0)
        self.assertEqual(self.group.sex, 'male')
        self.assertEqual(self.group.alive, False)

    def test_invalid(self):
        self.assertRaises(ValueError, self.group.load_dict,
                          {'id': '1', 'alive': 'not bool'})

    def test_set(self):
        self.group.set('name', 'bar')
        self.group.set('age', '123')
        self.assertEqual(self.group.name, 'bar')
        self.assertEqual(self.group.age, 123)


class TomlConfigTestCases(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.conf = get_toml_config()

    @mock.patch('toml.load')
    def test_load(self, mock_load):
        mock_load.return_value = {
            'debug': True,
            'log_file': 'demo.log',
            'list_option': 'value1',
            'people': {'id': '00001'},
        }
        self.conf.load('demo.conf')
        self.assertEqual(self.conf.debug, True)
        self.assertEqual(self.conf.log_file, 'demo.log')
        self.assertEqual(self.conf.list_option, ['value1'])
        self.assertEqual(self.conf.people.id, '00001')
        self.assertEqual(self.conf.people.name, 'foo')
        self.assertEqual(self.conf.people.age, 0)
        self.assertEqual(self.conf.people.sex, None)
        self.assertEqual(self.conf.people.alive, True)

    @mock.patch('toml.load')
    def test_load_not_in(self, mock_load):
        mock_load.return_value = {
            'debug': True,
            'people': {'id': '00001'},
        }
        self.conf.load('demo.conf')
        self.assertEqual(self.conf.debug, True)
        self.assertEqual(self.conf.log_file, None)
        self.assertEqual(self.conf.people.id, '00001')
        self.assertEqual(self.conf.people.name, 'foo')
        self.assertEqual(self.conf.people.age, 0)
        self.assertEqual(self.conf.people.sex, None)
        self.assertEqual(self.conf.people.alive, True)

    def test_set(self):
        self.conf.set('debug', True)
        self.assertEqual(self.conf.debug, True)

        self.conf.people.set('name', 'bar')
        self.conf.people.set('age', '123')
        self.assertEqual(self.conf.people.name, 'bar')
        self.assertEqual(self.conf.people.age, 123)
