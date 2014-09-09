"""Helper functions for using the FoLiA format from pynlpl. 
"""


from pynlpl.formats import folia


def parse_document(file_name):
    try:
        doc = folia.Document(file=file_name)
    except Exception as e:
        return None, 'Unable to parse FoLiA XML file.\n{}'.format(str(e))
    return doc, 'Successfully parsed FoLiA XML file.'
