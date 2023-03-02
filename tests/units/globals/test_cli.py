from easy2use.globals import cli
import unittest


class SubCliParserTestCases(unittest.TestCase):

    def test_add_command(self):
        parser = cli.SubCliParser('Test Command')

        @parser.add_command(cli.Arg('number1', type=int),
                            cli.Arg('number2', type=int))
        def number_plus(args):
            """Number Plus
            """
            pass
        self.assertIn('number-plus', parser.sub_parser._name_parser_map)
        arg_parser = parser.sub_parser._name_parser_map['number-plus']
        self.assertEqual('Number Plus', arg_parser.description)
        self.assertEqual(3, len(arg_parser._actions))
        self.assertEqual('help', arg_parser._actions[0].dest)
        self.assertEqual('number1', arg_parser._actions[1].dest)
        self.assertEqual('number2', arg_parser._actions[2].dest)
