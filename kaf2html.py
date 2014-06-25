"""Script to generate an HTML page from a KAF file that shows the text contents
including line numbers.
"""
from bs4 import BeautifulSoup


with open('data/minnenijd.kaf') as f:
    xml_doc = BeautifulSoup(f)

output_html = ['<html><head>',
               '<meta http-equiv="Content-Type" content="text/html; '
               'charset=utf-8">', '</head>', '<body>', '<p>']

current_para = None
new_para = False
current_sent = None

for token in xml_doc('wf'):
    if token['para'] != current_para:
        current_para = token['para']
        output_html.append('</p><p>')
        new_para = True
    if token['sent'] != current_sent:
        current_sent = token['sent']
        if not new_para:
            output_html.append('<br>')
        output_html.append(str(current_sent))
        output_html.append(': ')
        new_para = False

    # exctract text from cdata (waarom is dat nou weer zo!)
    output_html.append(token.text)

output_html.append('</p>')

html = BeautifulSoup(' '.join(output_html))
print html.prettify().encode('utf-8')
