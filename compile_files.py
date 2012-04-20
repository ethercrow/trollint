#!/usr/bin/env python
# encoding: utf-8

import sys
from clang import cindex
from utils import get_clang_args, get_clang_analyzer_diagnostics

if __name__ == '__main__':

    filenames = sys.argv[1:]

    clang_args = get_clang_args()

    clang_args = filter(lambda a: '-W' not in a, clang_args)

    # print clang_args

    for filename in filenames:
        index = cindex.Index.create()
        tu = index.parse(filename, clang_args)
        if not tu:
            print filename + " parsing failed"
            continue
        tu.reparse()

        for d in tu.diagnostics:
            if d.location.file and 'Developer/SDK' not in d.location.file.name:
                print(d.location.file.name + ':' + str(d.location.line)
                        + ' ' + d.spelling)
            else:
                # print('???:' + str(d.location.line) + ' ' + d.spelling)
                pass

        for d in get_clang_analyzer_diagnostics(filename, clang_args):
            print(d.filename + ':' + str(d.line_number) + ' ' + d.message)
