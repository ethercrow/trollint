
import os
from os.path import join

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

    for d in ('Classes', 'opt', 'src', 'geometry'):
        for root, dirs, files in os.walk(d):
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

    # TODO: parse xcode project file to see if
    # ARC is enabled for this file
    result += ['-fobjc-arc']

    # TODO: find pch more reliably
    # TODO: actually precompile this *pch*
    result += ['-include', 'clang.pch']

    for d in find_local_include_dirs():
        result += ['-I', d]

    return result
