import json
import click


@click.command()
@click.argument('json1', type=click.File())
@click.argument('json2', type=click.File())
def cli(json1, json2):
    data1 = json.load(json1)
    data2 = json.load(json2)

    print('File {}: {} events'.format(click.format_filename(json1), len(data1['timeline']['events'])))
    print('File {}: {} events'.format(click.format_filename(json2), len(data2['timeline']['events'])))

    # compare number of events
    if len(data1['timeline']['events']) != len(data2['timeline']['events']):
        print('Unequal number of events!')

    events1 = {}
    for e in data1['timeline']['events']:
        events1[e['event']] = e

    events2 = {}
    for e in data2['timeline']['events']:
        events2[e['event']] = e

    # compare event ids
    for el in events1.keys():
        if el not in events2.keys():
            print 'Key {} not in events2'.format(el)
    for el in events2.keys():
        if el not in events1.keys():
            print 'Key {} not in events1'.format(el)

    # compare mention lengths
    for k in events1.keys():
        m1 = events1[k]['mentions']
        m2 = events2[k]['mentions']

        if len(m1) != len(m2):
            print 'Unequal lenth of mentions for event {}'.format(k)



if __name__ == '__main__':
    cli()
