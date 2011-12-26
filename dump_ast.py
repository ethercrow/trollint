#!/usr/bin/env python
# encoding: utf-8

import sys
import clang.cindex as cindex


def print_cursor_recursive(cur, blob, depth=0):
    # print('{} {} | {}'.format(' '*4*depth, cur.kind, cur.displayname))
    print('{} {} | {}'.format(' ' * 4 * depth, cur.kind,
        blob[cur.extent.start.offset:cur.extent.end.offset]))
    for child in cur.get_children():
        print_cursor_recursive(child, blob, depth + 1)


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

    print_cursor_recursive(tu.cursor, blob)
