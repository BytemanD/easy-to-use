from easy2use.globals import cli
import unittest


class SubCliParserTestCases(unittest.TestCase):

    def test_add_command(self):
        parser = cli.SubCliParser('Test Command')

        @parser.add_command(cli.Arg('arg1'), cli.Arg('arg2'))
        def cmd_1(args):
            """Command 1
            """
            pass

        @parser.add_command(cli.Arg('arg3'), cli.Arg('arg4'))
        def cmd_2(args):
            """Command 2
            """
            pass

        self.assertIn('cmd-1', parser.sub_parser._name_parser_map)
        parser1 = parser.sub_parser._name_parser_map['cmd-1']
        self.assertEqual('Command 1', parser1.description)
        self.assertEqual(3, len(parser1._actions))
        self.assertEqual('help', parser1._actions[0].dest)
        self.assertEqual('arg1', parser1._actions[1].dest)
        self.assertEqual('arg2', parser1._actions[2].dest)

        self.assertIn('cmd-2', parser.sub_parser._name_parser_map)
        parser2 = parser.sub_parser._name_parser_map['cmd-2']
        self.assertEqual('Command 2', parser2.description)
        self.assertEqual(3, len(parser2._actions))
        self.assertEqual('help', parser2._actions[0].dest)
        self.assertEqual('arg3', parser2._actions[1].dest)
        self.assertEqual('arg4', parser2._actions[2].dest)
