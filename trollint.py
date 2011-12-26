#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import clang.cindex as cindex
import config
import passes.base.pass_base
from progressbar import progressbar
from diagnostic import from_clang_diagnostic
import report
from itertools import groupby


def discover_pass_classes():
    import imp
    passes_dir = os.path.join(os.path.dirname(sys.argv[0]), 'passes')
    module_names = [f for f in os.listdir(passes_dir)
                         if f.endswith('.py') and f != '__init__.py']
    modules = [imp.load_source('passes.' + m.replace('.py', ''),
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


def collect_lint_diagnostics(filename, pass_classes, clang_args):

    try:
        with open(filename) as fi:
            blob = fi.read()
    except IOError:
        print('Could not open file {0}'.format(filename))
        return []

    index = cindex.Index.create()
    tu = index.parse(filename, clang_args)

    diags = []
    # diags += [from_clang_diagnostic(d, filename) for d in tu.diagnostics]

    for pass_class in pass_classes:

        p = pass_class()

        if not p.enabled:
            continue

        if 'config' in pass_class.needs:
            p.config = config.Config()

        if 'cursor' in pass_class.needs:
            p.cursor = tu.cursor

        if 'text' in pass_class.needs:
            p.text = blob

        if 'filename' in pass_class.needs:
            p.filename = filename

        diags += p.get_diagnostics()

    return diags


if __name__ == '__main__':

    filenames = sys.argv[1:]

    pass_classes = discover_pass_classes()
    try:
        with open('.clang_complete') as fi:
            clang_args = [l.rstrip() for l in fi.readlines()]
    except IOError:
        clang_args = []

    diags = []

    for filename in progressbar(filenames):
        diags += collect_lint_diagnostics(filename, pass_classes, clang_args)

    diags = sorted(diags, key=lambda d: d.line_number)
    diags = sorted(diags, key=lambda d: d.filename)

    def poor_man_unique(xs):
        if not xs:
            return []
        result = xs[0:1]
        for x in xs:
            if x != result[-1]:
                result.append(x)
        return result

    diags = poor_man_unique(diags)

    def group_diagnostics_by_files(ds):

        def file_from_group(g):
            return {'name': g[0], 'diagnostics': list(g[1])}

        result = [file_from_group(g) for g in groupby(ds,
                                                      lambda d: d.filename)]
        return result

    files_with_diags = group_diagnostics_by_files(diags)

    report.render_to_directory('report', 'OHai', files_with_diags)

    if not diags:
        print('all clear')
