#!/usr/bin/python3

import sys
import contextlib
from argparse import ArgumentParser
from utils import MAN2HTML


def get_arguments():
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', metavar='FILE',
                        help='Input file (e.g. tmp.txt)', required=True)
    parser.add_argument('-o', '--output', dest='output', metavar='FILE',
                        help='Output file (e.g. tmp.html)')
    parser.add_argument('-s', '--style', dest='style', metavar='FILE',
                        help='Styles file (e.g. style.css)')
    args = parser.parse_args()
    return args


@contextlib.contextmanager
def file_open(filename=None):
    opened_file = open(filename, 'w') if filename else sys.stdout
    try:
        yield opened_file
    finally:
        if opened_file is not sys.stdout:
            opened_file.close()

if __name__ == '__main__':
    arguments = get_arguments()
    with open(arguments.input) as f:
        man_text = f.readlines()
    if arguments.style:
        with open(arguments.style) as f:
            styles = f.read()
    else:
        styles = ''
    with file_open(arguments.output) as f:
        converter = MAN2HTML()
        f.write(converter.man2html(man_text, styles=styles))
