'''
Very simple tool to convert rst fields to html

TODO: make generic
'''

from docutils.core import publish_parts
from tempfile import NamedTemporaryFile

# see http://docutils.sourceforge.net/docs/user/config.html
default_rst_opts = {
    'no_generator': True,
    'no_source_link': True,
    'tab_width': 4,
    'file_insertion_enabled': True,
    'raw_enabled': True,
    'stylesheet_path': None,
    'traceback': False,
    'halt_level': 2,
}

TEMPLATE = '''
%(body)s
'''


def rst2html(rst, opts=None):
    '''Simple tool to convert rst to html to be embeded in any document

    Example:

        >>> chain = "Text in rst"
        >>> rst2html(chain)
        u'<div class="document">\\n<p>Text in rst</p>\\n</div>\\n'

    @param: rst Text multiline in rst format
    '''
    template = NamedTemporaryFile('w', suffix='.txt', delete=False)
    rst_opts = default_rst_opts.copy()
    if opts:
        rst_opts.update(opts)
    template.write(TEMPLATE)
    template.close()
    rst_opts['template'] = template.name
    out = publish_parts(rst,
                        writer_name='html',
                        settings_overrides=rst_opts)['html_body']
    return out

if __name__ == '__main__':
    import doctest
    doctest.testmod()
