#!/usr/bin/env python
# encoding: utf-8

import sys
import clang.cindex as cindex
from utils import full_text_for_cursor, get_clang_args


def print_cursor_recursive(cur, depth=0):

    token_text = full_text_for_cursor(cur)
    token_text = cur.displayname

    print('{0} {1} | {2}'.format('->' * depth, cur.kind, token_text,
        cur.location.file.name if cur.location.file else '???'))

    for child in cur.get_children():
        print_cursor_recursive(child, depth + 1)


if __name__ == '__main__':

    filename = sys.argv[1]

    index = cindex.Index.create()
    tu = index.parse(filename, get_clang_args())

    with open(filename) as fi:
        blob = fi.read()

    print_cursor_recursive(tu.cursor)
