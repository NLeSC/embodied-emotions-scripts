import json
import click
import glob
import os
import pandas as pd

from codecs import open

from naf2json import merge_events


def combine_events(result, to_merge):
    events = {}
    for e in to_merge['timeline']['events']:
        events[e['event']] = e

    # merge events that have the same id
    new_events = []
    for event in result['timeline']['events']:
        event_id = event['event']
        if event_id in events.keys():
            new_events.append(merge_events(event, events[event_id]))
            del events[event_id]
        else:
            new_events.append(event)

    # add remaining events
    for event, data in events.iteritems():
        new_events.append(data)

    result['timeline']['events'] = new_events

    return result


@click.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('metadata', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
def cli(input_dir, metadata, output_file):
    output_dir = os.path.dirname(click.format_filename(output_file))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    metadata = pd.read_csv(metadata, header=None, sep='\\t', index_col=0,
                           encoding='utf-8', engine='python')

    json_files = glob.glob('{}/*.json'.format(input_dir))
    print('Found {} json files'.format(len(json_files)))

    data = None

    for i, fi in enumerate(json_files):
        print '{} ({} of {})'.format(fi, (i + 1), len(json_files))
        text_id = os.path.basename(fi).split('.')[0].replace('.json', '')
        print text_id
        with open(fi, 'r', encoding='utf-8') as f:
            t = json.load(f)

        if not data:
            data = t
        else:
            # merge events
            data = combine_events(data, t)

            # merge source texts
            data['timeline']['sources'].append(t['timeline']['sources'][0])

    with open(output_file, 'wb', encoding='utf-8') as f:
        json.dump(data, f, sort_keys=True, indent=4)


if __name__ == '__main__':
    cli()
