#!/usr/bin/env python
# encoding: utf-8

import sys
import clang.cindex as cindex
from utils import full_text_for_cursor

def print_cursor_recursive(cur, depth=0):

    token_text = full_text_for_cursor(cur)

    print('{0} {1} | {2}'.format(' ' * 4 * depth, cur.kind, token_text))

    for child in cur.get_children():
        print_cursor_recursive(child, depth + 1)


if __name__ == '__main__':

    filename = sys.argv[1]

    try:
        with open('.clang_complete') as fi:
            clang_args = [l.rstrip() for l in fi.readlines()]
    except IOError:
        clang_args = []

    index = cindex.Index.create()
    tu = index.parse(filename, clang_args)

    with open(filename) as fi:
        blob = fi.read()

    print_cursor_recursive(tu.cursor)
