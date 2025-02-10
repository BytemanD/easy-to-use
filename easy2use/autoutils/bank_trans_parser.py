

import argparse
import re

import prettytable
import importlib

fitz = None

class BankTransactionHistoryParser(object):

    def __init__(self, headers, calculate_total_trans_amount=None):
        self.headers = headers
        self.table = prettytable.PrettyTable(self.headers)
        self.calculate_total_trans_amount = calculate_total_trans_amount
        self._total_trans_amount = 0

    def parse(self, pdf_file):
        self._total_trans_amount = 0
        pdf_document = fitz.open(pdf_file)
        page = pdf_document.load_page(0)  # 加载第一页
        text = page.get_text()
        for row in self.get_rows_from_page(text):
            self.table.add_row(row)
            self._total_trans_amount += self.calculate_total_trans_amount(row)

    def get_rows_from_page(self, text):
        raise NotImplementedError()

    def count(self):
        return self.table.rowcount

    def total_trans_amount(self):
        if self.calculate_total_trans_amount is None:
            raise NotImplementedError()
        return self._total_trans_amount


class SuZhou(BankTransactionHistoryParser):

    def __init__(self):
        super(SuZhou, self).__init__(
            ["交易日期", '交易金额', "摘要", '账户余额', '对方户名'],
            calculate_total_trans_amount=lambda row: float(row[1])
        )
        self.table.align['交易金额'] = 'r'

    def get_rows_from_page(self, text :str):
        matched = re.findall(
            r'([0-9]+)\n([\-+\.0-9]+)\n(.*)\n([-+\.0-9]+)\n[0-9]*(.*)', text)
        rows = []
        for item in matched:
            record = list(item)
            if len(record) < 5:
                record.extend(['' for _ in range(5 - len(record))])
            rows.append(record)
        return rows

def parse_suzhou(args):
    his_Parser = SuZhou()
    his_Parser.parse(args.file)
    print(his_Parser.table)
    print(f"合计 {his_Parser.count()} 条记录, 交易金额: "
          f"{his_Parser.total_trans_amount():.2f}")


def main():
    parser = argparse.ArgumentParser(description='解析银行交易流水的PDF文件')

    subparsers = parser.add_subparsers()
    suzhou_parser = subparsers.add_parser('suzhou', help="苏州银行")
    suzhou_parser.add_argument("file")
    suzhou_parser.set_defaults(func=parse_suzhou)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()

    global fitz
    try:
        fitz = importlib.import_module('fitz')
    except ImportError:
        print("ERROR: package fitz is required")
        exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
