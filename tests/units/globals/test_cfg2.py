from easy2use.globals import cfg2
import unittest


def get_option_group():

    class OptionGroupDemo(cfg2.OptionGroup):
        id = cfg2.Option('id', required=True)
        name = cfg2.Option('name', default='foo')
        age = cfg2.IntOption('age', default=0)
        sex = cfg2.Option('sex')
        alive = cfg2.BoolOption('alive', default=True)

    return OptionGroupDemo()


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
