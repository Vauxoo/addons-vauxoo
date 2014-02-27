# -*- coding: utf-8 -*-
def get_encodings(hint_encoding='utf-8'):
    fallbacks = {
        'latin1': 'latin9',
        'iso-8859-1': 'iso8859-15',
        'cp1252': '1252',
    }
    if hint_encoding:
        yield hint_encoding
        if hint_encoding.lower() in fallbacks:
            yield fallbacks[hint_encoding.lower()]

    # some defaults (also taking care of pure ASCII)
    for charset in ['utf8', 'latin1']:
        if not (hint_encoding) or (charset.lower() != hint_encoding.lower()):
            yield charset

    from locale import getpreferredencoding
    prefenc = getpreferredencoding()
    if prefenc and prefenc.lower() != 'utf-8':
        yield prefenc
        prefenc = fallbacks.get(prefenc.lower())
        if prefenc:
            yield prefenc


def ustr(value, hint_encoding='utf-8'):
    """This method is similar to the builtin `str` method, except
       it will return unicode() string.

    @param value: the value to convert
    @param hint_encoding: an optional encoding that was detected
                          upstream and should be tried first to
                          decode ``value``.

    @rtype: unicode
    @return: unicode string
    """
    if isinstance(value, Exception):
        return exception_to_unicode(value)

    if isinstance(value, unicode):
        return value

    if not isinstance(value, basestring):
        try:
            return unicode(value)
        except Exception:
            raise UnicodeError('unable to convert %r' % (value,))

    for ln in get_encodings(hint_encoding):
        try:
            return unicode(value, ln)
        except Exception:
            pass
    raise UnicodeError('unable to convert %r' % (value,))


def exception_to_unicode(e):
    if (sys.version_info[:2] < (2, 6)) and hasattr(e, 'message'):
        return ustr(e.message)
    if hasattr(e, 'args'):
        return "\n".join((ustr(a) for a in e.args))
    try:
        return unicode(e)
    except Exception:
        return u"Unknown message"

print ustr('hóla')
