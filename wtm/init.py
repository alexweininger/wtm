import click
from repos import repos, group1


@click.group()
def cli():
    pass


cli.add_command(repos)
cli.add_command(group1)

if __name__ == '__main__':
    cli()