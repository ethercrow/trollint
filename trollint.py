#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import clang.cindex as cindex
import config
import passes.base.pass_base

def discover_pass_classes():
    import imp
    passes_dir = os.path.join(os.path.dirname(sys.argv[0]), 'passes')
    module_names = [f for f in os.listdir(passes_dir)
                         if f.endswith('.py') and f != '__init__.py']
    modules =  [imp.load_source('passes.' + m.replace('.py', ''),
                            os.path.join(passes_dir, m)) for m in module_names]

    def extract(m):
        result = []
        for maybe_class_name in dir(m):
            if 'Base' in maybe_class_name:
                continue
            maybe_class = getattr(m, maybe_class_name)
            if isinstance(maybe_class, type)\
                    and issubclass(maybe_class, passes.base.pass_base.PassBase):
                result.append(maybe_class)
        return result

    return sum([extract(m) for m in modules], [])


if __name__ == '__main__':

    filename = sys.argv[1]

    try:
        with open('.clang_complete') as fi:
            clang_args = [l.rstrip() for l in fi.readlines()]
    except IOError:
        clang_args = []

    try:
        with open(filename) as fi:
            blob = fi.read()
    except IOError:
        print('Could not open file {}'.format(filename))
        sys.exit(-1)

    index = cindex.Index.create()
    tu = index.parse(filename, clang_args)

    pass_classes = discover_pass_classes()

    diags = []

    for pass_class in pass_classes:

        p = pass_class()

        if 'config' in pass_class.needs:
            p.config = config.Config()

        if 'cursor' in pass_class.needs:
            p.cursor = tu.cursor

        if 'text' in pass_class.needs:
            p.text = blob

        if 'filename' in pass_class.needs:
            p.filename = filename

        diags += p.get_diagnostics()

    diags = sorted(diags, key=lambda d: d.line_number)
    diags = sorted(diags, key=lambda d: d.filename)

    if diags:
        print('\n'.join('    '+str(d) for d in diags))
    else:
        print('all clear')

