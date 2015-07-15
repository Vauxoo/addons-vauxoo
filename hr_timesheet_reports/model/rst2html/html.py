'''
Very simple tool to convert rst fields to html

TODO: make generic
'''

from docutils.core import publish_string

from openerp import modules

# see http://docutils.sourceforge.net/docs/user/config.html
default_rst_opts = {
    'no_generator': True,
    'no_source_link': True,
    'tab_width': 4,
    'file_insertion_enabled': False,
    'raw_enabled': False,
    'stylesheet_path': None,
    'traceback': True,
    'halt_level': 5,
}


def rst2html(rst, opts=None):
    rst_opts = default_rst_opts.copy()
    if opts:
        rst_opts.update(opts)
    # TODO: this should be a parameter
    rst_opts['template'] = modules.get_module_resource('vauxoo_sale_reports',
                                                       'model/rst2html',
                                                       'template.txt')
    out = publish_string(rst, writer_name='html', settings_overrides=rst_opts)
    return out

if __name__ == '__main__':
    print rst2html("""
                   - Hola
                   - Mundo
                   """)
