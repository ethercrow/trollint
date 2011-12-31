#!/usr/bin/env python
# encoding: utf-8

import sys
from clang import cindex
from utils import get_clang_args


if __name__ == '__main__':

    filename = sys.argv[1]

    clang_args = get_clang_args()

    clang_args = filter(lambda a: '-W' not in a, clang_args)

    print clang_args

    index = cindex.Index.create()
    tu = index.parse(filename, clang_args)
    tu.reparse()

    for d in tu.diagnostics:
        if d.location.file:
            print d.location.file.name + ':' + str(d.location.line) + ' ' + d.spelling
        else:
            print '???:' + str(d.location.line) + ' ' + d.spelling
