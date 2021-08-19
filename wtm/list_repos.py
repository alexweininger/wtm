#!/usr/bin/env python
"""
find all git repositories (and git working directories) starting from the
current directory and perform a 'git fsck' on them.
"""

from __future__ import division, print_function

import contextlib
import os
import subprocess


def git_directories(startdir):
    for dirpath, dirnames, _ in os.walk(startdir):
        if set(['info', 'objects', 'refs']).issubset(set(dirnames)):
            yield dirpath


@contextlib.contextmanager
def working_directory(directory):
    saved_cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(saved_cwd)


for git_directory in git_directories(os.path.expanduser('~/dev/worktrees/')):
    with working_directory(git_directory):
        print('\n{}:'.format(os.getcwd()))