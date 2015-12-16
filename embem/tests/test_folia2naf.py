from nose.tools import assert_equal

from lxml.etree import Element, tostring, fromstring

from embem.kafnaftag.folia2naf import create_linguisticProcessor


def test_create_linguisticProcessor_without_existing_lp():
    layer = 'emotions'
    lps = {'rakel-heem-spelling_normalized': '1.0'}
    timestamp = '2015-11-19 11:47:05.080952'
    header = fromstring('<nafHeader></nafHeader>')

    create_linguisticProcessor(layer, lps, timestamp, header)

    expected = '<nafHeader>' \
               '<linguisticProcessors layer="emotions">' \
               '<lp name="rakel-heem-spelling_normalized" timestamp="2015-11-19 11:47:05.080952" version="1.0"/>' \
               '</linguisticProcessors>' \
               '</nafHeader>'
    assert_equal(expected, tostring(header))


def test_create_linguisticProcessor_with_existing_lp():
    layer = 'emotions'
    lps = {'rakel-heem-spelling_normalized': '1.0'}
    timestamp = '2015-11-19 11:47:05.080952'
    header = fromstring('<nafHeader>'
                        '<linguisticProcessors layer="emotions">'
                        '<lp name="heem-expand-body_parts" timestamp="2015-11-19 11:47:05.080952" version="1.0"/>'
                        '</linguisticProcessors>'
                        '</nafHeader>')

    create_linguisticProcessor(layer, lps, timestamp, header)

    expected = '<nafHeader>' \
               '<linguisticProcessors layer="emotions">' \
               '<lp name="heem-expand-body_parts" timestamp="2015-11-19 11:47:05.080952" version="1.0"/>' \
               '<lp name="rakel-heem-spelling_normalized" timestamp="2015-11-19 11:47:05.080952" version="1.0"/>' \
               '</linguisticProcessors>' \
               '</nafHeader>'
    assert_equal(expected, tostring(header))
