import click
import git_utils
import os
import os.path
import json

WORKTREE_DIR = os.path.expanduser('~/dev/worktrees/')
WORKTREE_FILE = os.path.join(WORKTREE_DIR, '.worktrees.json')

def get_worktrees_file():
    if not os.path.exists(WORKTREE_FILE):
        with open(WORKTREE_FILE, 'w') as f:
            json.dump({}, f)
            f.close()
    else:
        with open(WORKTREE_FILE, 'r') as f:
            worktrees = json.load(f)
            f.close()
            return worktrees

def write_worktrees_file(main_trees, linked_trees):
    worktrees = get_worktrees_file()

    for main_tree in main_trees:
        linked = {}
        for link in linked_trees:
            if link['fullname'].find(main_tree['name']) != -1:
                linked[link['name']] = link
        tree = {
            'main': main_tree,
            'linked': linked
        }
        worktrees[main_tree['name']] = tree


    with open(WORKTREE_FILE, 'w') as f:
            json.dump(worktrees, f, indent=4)
            f.close()
    
def gitCommand(str):
    stream = os.popen(str)
    output = stream.read()
    return output

def npmInstall(path):
    stream = os.popen(f"npm install --prefix {path}")
    output = stream.read()
    return output

def get_worktrees(repo='', path=os.getcwd()):
    path = os.path.normpath(path)
    lines = gitCommand(f'git --git-dir {path}/.git worktree list --porcelain').split('\n')
    worktree_paths = []
    for wt in lines:
        if wt.find('worktree') != -1:
            worktree_paths.append(wt.split(' ')[1])

    main_worktrees = []
    linked_worktrees = []
    for path in worktree_paths:
        if path.find('worktree') != -1:
            short_path = path.replace(WORKTREE_DIR, '')
            linked_worktrees.append({
                'name': os.path.basename(path),
                'fullname': short_path,
                'path': path
            })
        else:
            name = os.path.basename(path)
            main_worktrees.append({
                'name': name,
                'path': path
            })

    repo_main = None
    repo_linked = []

    if repo != '':
        repo_main_idx = main_worktrees.index(repo)
        repo_main = main_worktrees[repo_main_idx]
        repo_linked = list(filter(lambda x: x.find(repo) != -1, linked_worktrees))
        return [repo_main], repo_linked
    else:
        return main_worktrees, linked_worktrees

@click.group()
@click.option('--verbose/--no-verbose', default=False, help='Enable verbose mode')
@click.option('--raw/--no-raw', default=False, help='Enable raw mode')
@click.pass_context
def repos(ctx, verbose, raw):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj['VERBOSE'] = verbose
    ctx.obj['RAW'] = raw

@click.group()
@click.option('--verbose/--no-verbose', default=False, help='Enable verbose mode')
@click.option('--raw/--no-raw', default=False, help='Enable raw mode')
@click.pass_context
def group1(ctx, verbose, raw):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj['VERBOSE'] = verbose
    ctx.obj['RAW'] = raw

@group1.command()
@click.pass_context
@click.argument('branch', required=False)
@click.option('--path', default=WORKTREE_DIR, help='Location to create worktree at')
@click.option('--i', 'install', flag_value=True, help='Run npm install in the directory.')
def add(ctx, path, install, branch):
    """Creates a worktree at specified path, creating a branch with specified name."""
    worktree_name = branch.replace('alex/', '')
    remote_name = git_utils.get_remote_name()

    worktree_path = os.path.join(path, remote_name, worktree_name)

    click.echo(f"Creating branch {branch} at {worktree_path}.")

    git_command = f"git worktree add {worktree_path} -b {branch}"
    if (ctx.obj['VERBOSE']):
        print(git_command)
    output = gitCommand(git_command)
    print(output)

    success = output.find('fatal') == -1
    if success:
        if install:
            click.echo(f"Running npm install in {worktree_path}")
            npmInstall(worktree_path)

group1.add_command(add)

@group1.command('list')
@click.option('--local', 'local', flag_value=True, help='Run npm install in the directory.')
@click.pass_context
def list(ctx, local):
    """Lists all git worktrees."""

    if local:
        get_worktrees()
        return

    git_command = f"git worktree list"
    if (ctx.obj['VERBOSE']):
        print(git_command)

    output = gitCommand(git_command)

    if (ctx.obj['RAW']):
        print(output)
    else:
        print(output.replace('/Users/alex', '~'))

group1.add_command(list)

@repos.command('list')
@click.option('--local', 'local', flag_value=True, help='Run npm install in the directory.')
@click.pass_context
def repos_list(ctx, local):
    """Lists all git worktrees."""

    worktrees = get_worktrees_file()
    click.echo('\n'.join([tree for tree in worktrees]))

repos.add_command(repos_list)

@group1.command()
@click.pass_context
def update(ctx):
    """Lists all git worktrees."""

    mains, linked = get_worktrees()
    write_worktrees_file(mains, linked)

group1.add_command(update)

@group1.command()
@click.pass_context
@click.argument('path', required=True, default=os.getcwd())
def register(ctx, path):
    """Lists all git worktrees."""
    click.echo(path)
    mains, linked = get_worktrees(path=path)
    print('mains ', mains, 'linked ', linked)
    write_worktrees_file(mains, linked)

group1.add_command(register)

@group1.command('open')
@click.pass_context
@click.argument('repo', required=True, default=os.path.basename(os.path.abspath(os.getcwd())))
@click.argument('tree', required=True, default='main')
def openWt(ctx, repo, tree):
    """Opens a worktree"""

    worktrees = get_worktrees_file()
    worktree = worktrees[repo]

    path = worktree['main']['path']
    if tree != 'main':
        path = worktree['linked'][tree]['path']
    
    command = f'code-insiders {path}'
    print(command)
    gitCommand(command)

group1.add_command(openWt)

cli1 = click.CommandCollection(sources=[repos, group1])
if __name__ == '__main__':
    cli1()