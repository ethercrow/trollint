#!/usr/bin/env python
# encoding: utf-8

import sys
import os
from utils import get_clang_args

if __name__ == '__main__':

    if os.path.exists('.clang_complete') and '--force' not in sys.argv:
        print('.clang_complete already exists')
        print('invoke with --force to rewrite')
        sys.exit(1)

    clang_args = get_clang_args()

    formatted_clang_args = ' '.join(clang_args).replace(' -', '\n-').lstrip()

    with open('.clang_complete', 'w') as fo:
        fo.write(formatted_clang_args)
