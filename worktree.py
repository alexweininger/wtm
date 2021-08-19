import click
from git import Repo

import os

def gitCommand(str):
    stream = os.popen(str)
    output = stream.read()
    return output

@click.command()
@click.option('--name', help='Worktree name')
@click.option('--path', default='~/dev/worktrees/', help='Location to create worktree at.')
@click.option('--branch', prompt='Branch name:', help='The name of the branch to create.')
def hello(name, path, branch):
    """Creates a worktree at specified path, creating a branch with specified name."""
    worktree_name = name if name != None else branch.replace('alex/', '')
    click.echo(f"Creating branch {branch} at {path + worktree_name}.")

    git_command = f"git worktree add {path + worktree_name} -b {branch}"
    print(git_command)
    output = gitCommand(git_command)
    print(output)

if __name__ == '__main__':
    hello()

# bare_repo = Repo('.')
# assert not bare_repo.is_dirty()  # check the dirty state
# print(bare_repo.untracked_files)