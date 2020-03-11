XLS Report Controller
=====================

This module does nothing by itself is meant to be imported by other modules to
enable them to export their QWeb reports into XLS format. The export tries to interpret
the cssstyle defined on qweb template and layouts into a XLWT Style. Not all the cssstyles
are mapped, so if you spot one, please contact us to add it. Special treatment on qweb
template and layouts is required to leverage from this module, meaning the style defined
should be flat, there is no support for cascading styles.

Contributors
------------

* Fekete Mihai <feketemihai@gmail.com>
