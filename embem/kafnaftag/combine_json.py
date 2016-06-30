import json
import click


@click.command()
@click.argument('input_file', type=click.File())
@click.argument('output_file', type=click.Path())
def cli(input_file, output_file):
    data = json.load(input_file)
    print len(data['timeline']['events'])

if __name__ == '__main__':
    cli()
