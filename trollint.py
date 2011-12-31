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
from utils import get_clang_args


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
    parse_opts = cindex.TranslationUnit.PrecompiledPreamble

    tu = index.parse(filename, clang_args, options=parse_opts)

    diags = []
    diags += [from_clang_diagnostic(d, filename) for d in tu.diagnostics]

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


def collect_all_lint_diagnostics(filenames, pass_classes, clang_args):

    diags = []

    for filename in progressbar(filenames):
        diags += collect_lint_diagnostics(filename, pass_classes, clang_args)

    diags = sorted(diags, key=lambda d: d.line_number)
    diags = sorted(diags, key=lambda d: d.filename)

    # is there a standard function to do this?
    def unique(xs):
        if not xs:
            return []
        result = xs[0:1]
        for x in xs:
            if x != result[-1]:
                result.append(x)
        return result

    return unique(diags)

if __name__ == '__main__':

    filenames = sys.argv[1:]

    pass_classes = discover_pass_classes()

    clang_args = get_clang_args()

    diags = collect_all_lint_diagnostics(filenames, pass_classes, clang_args)

    category_names = list(set([d.category for d in diags]))

    def group_diagnostics(ds):

        def file_from_group(g):
            name = g[0]

            categories = {}
            for cname in category_names:
                categories[cname] = []

            for cat, ds in groupby(g[1], lambda d: d.category):
                categories.update({cat: list(ds)})
            return {'name': name, 'diagnostic_groups': categories}

        result = [file_from_group(g) for g in groupby(ds, lambda d: d.filename)
                                     if not os.path.isabs(g[0])
                ]
        return result

    files_with_categorized_diags = group_diagnostics(diags)

    report.render_to_directory('report', 'OHai',
            files_with_categorized_diags, category_names)

    if not diags:
        print('all clear')
