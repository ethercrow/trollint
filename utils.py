
import os
from os.path import join

DEFAULT_WARNINGS = ['-Wall', '-Wextra', '-Wshadow',
                    '-Winitializer-overrides',
                    '-Wsemicolon-before-method-body ',
                    '-Widiomatic-parentheses', '-Wdeprecated', '-Wdiv-by-zero',
                    '-Wcomments', '-Wempty-body', '-Wextra-tokens',
                    '-Wmissing-declarations', '-Wnull-dereference',
                    '-Wnonnull', '-Wtautological-compare',
                    '-Wprotocol', '-Wnonfragile-abi2',
                    '-Wno-conversion', '-Wno-missing-field-initializers',
                    '-Wno-unused-parameter', '-Wno-sign-compare',
                    '-Wno-sentinel', '-Wunreachable-code',
                    '-Wno-missing-braces'
                   ]


def full_text_for_cursor(cur):
    if cur.location.file:
        with open(cur.location.file.name) as fi:
            e = cur.extent
            text = fi.read()[e.start.offset:e.end.offset]
            return text
    else:
        return cur.displayname


def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def get_clang_basedir():

    clang_binary_path = which('clang')

    if clang_binary_path:
        return os.path.dirname(clang_binary_path)
    else:
        return None


def get_sdk_dir():
    candidates = [
        '/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs',
        join(os.environ['HOME'],
            'Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs'),
    ]

    for cand in candidates:
        if os.path.exists(cand):
            # choose latest sdk
            return join(cand, sorted(os.listdir(cand))[-1])
    else:
        return None


def find_local_include_dirs():

    result = []

    for root, dirs, files in os.walk('.'):
        if any((f.endswith('.h') for f in files)):
            result.append(root)

    return result


def get_clang_args():

    clang_basedir = get_clang_basedir()

    if not clang_basedir:
        print('clang base dir not found')

    clang_include_path = os.path.join(clang_basedir,
            '..', 'lib/clang/3.0/include')

    # guess SDK root
    sdk = get_sdk_dir()

    if not sdk:
        print('SDK not found')
        return []

    result = []
    result += ['-isysroot', sdk]
    result += ['-isystem', clang_include_path]
    result += ['-F', join(sdk, 'System/Library/Frameworks')]
    result += ['-I', join(sdk, 'usr/include')]

    result += ['-D', '__MACH__']
    result += ['-D', '__APPLE_CC__']
    result += ['-D', '__IPHONE_OS_VERSION_MIN_REQUIRED=40300']

    # enable modern objc features
    result += ['-fblocks', '-fobjc-nonfragile-abi']
    result += ['-fno-builtin']

    # force 32bit arch even if we are on 64bit host
    result += ['-m32']

    # TODO: ARC should be set per-file
    for maybe_projdir in os.listdir('.'):
        if maybe_projdir.endswith('.xcodeproj'):
            with open(join(maybe_projdir, 'project.pbxproj')) as fi:
                if 'CLANG_ENABLE_OBJC_ARC = YES' in fi.read():
                    result += ['-fobjc-arc']
                    break

    # TODO: find pch more reliably
    # TODO: actually precompile this *pch*
    for maybe_pch in os.listdir('.'):
        if maybe_pch.endswith('.pch'):
            result += ['-include', maybe_pch]

    result += DEFAULT_WARNINGS

    for d in find_local_include_dirs():
        result += ['-I', d]

    return result

# is there a standard function to do this?
def unique(xs):
    if not xs:
        return []
    result = xs[0:1]
    for x in xs:
        if x != result[-1]:
            result.append(x)
    return result

