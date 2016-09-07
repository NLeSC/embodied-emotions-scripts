import json
import click
import glob
import os
import copy

from codecs import open

from embem.machinelearningdata.count_labels import corpus_metadata

from naf2json import merge_events, json_out


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
@click.argument('output_dir', type=click.Path())
@click.option('--save-per', prompt='How to divide the output over files? (options: single-file, emotion)', default='single-file', type=click.Choice(['single-file', 'emotion']))
def cli(input_dir, metadata, output_dir, save_per):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    text2period, text2year, text2genre, period2text, genre2text = \
        corpus_metadata(metadata)

    json_files = glob.glob('{}/*.json'.format(input_dir))
    print('Found {} json files'.format(len(json_files)))

    data = {}

    for i, fi in enumerate(json_files):
        print '{} ({} of {})'.format(fi, (i + 1), len(json_files))
        text_id = os.path.basename(fi).split('.')[0].replace('.json', '')
        print text_id
        with open(fi, 'r', encoding='utf-8') as f:
            t = json.load(f)

        data_text = {}

        year = text2year[text_id]

        # change event ids to year, so the events can be merged by year
        for event in t['timeline']['events']:
            parts = event['event'].split('_')
            emotion = parts[0]
            bodyparts = parts[1]

            if save_per == 'single-file':
                label = 'all'
            elif save_per == 'emotion':
                label = emotion

            if label not in data_text.keys():
                data_text[label] = copy.deepcopy(json_out)

            new_id = '{}_{}_{}'.format(emotion, bodyparts, year)
            event['event'] = new_id
            print new_id

            data_text[label]['timeline']['events'].append(event)

        for label in data_text.keys():
            if not data.get(label):
                data[label] = data_text[label]
            else:
                # merge events
                data[label] = combine_events(data[label], data_text[label])

    print
    for label, d in data.iteritems():
        print 'Writing data for label "{}"'.format(label)
        print 'Number of events in result: {}'.format(len(d['timeline']['events']))

        output_file = os.path.join(output_dir, '{}.json'.format(label))
        with open(output_file, 'wb', encoding='utf-8') as f:
            json.dump(data[label], f, sort_keys=True, indent=4)


if __name__ == '__main__':
    cli()
