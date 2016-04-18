# -*- encoding: utf-8 -*-

from xlwt import XFStyle, Borders, Pattern, Font, Alignment

excel_color_map = {
    'rgb(0, 0, 0)': -7,
    'rgba(0, 0, 0, 0)': -7,
    'rgb(255, 255, 255)': 2,
    'rgb(255, 0, 0)': 3,
    'rgb(0, 255, 0)': 4,
    'rgb(0, 0, 255)': 5,
    'rgb(255, 255, 0)': 6,
    'rgb(255, 0, 255)': 7,
    'rgb(0, 255, 255)': 8,
    'rgb(128, 0, 0)': 9,
    'rgb(0, 128, 0)': 10,
    'rgb(0, 0, 128)': 11,
    'rgb(128, 128, 0)': 12,
    'rgb(128, 0, 128)': 13,
    'rgb(0, 128, 128)': 14,
    'rgb(192, 192, 192)': 15,
    'rgb(128, 128, 128)': 16,
    'rgb(153, 153, 255)': 17,
    'rgb(153, 51, 102)': 18,
    'rgb(255, 255, 204)': 19,
    'rgb(204, 255, 255)': 20,
    'rgb(102, 0, 102)': 21,
    'rgb(255, 128, 128)': 22,
    'rgb(0, 102, 204)': 23,
    'rgb(204, 204, 255)': 24,
    'rgb(0, 0, 128)': 25,
    'rgb(255, 0, 255)': 26,
    'rgb(255, 255, 0)': 27,
    'rgb(0, 255, 255)': 28,
    'rgb(128, 0, 128)': 29,
    'rgb(128, 0, 0)': 30,
    'rgb(0, 128, 128)': 31,
    'rgb(0, 0, 255)': 32,
    'rgb(0, 204, 255)': 33,
    'rgb(204, 255, 255)': 34,
    'rgb(204, 255, 204)': 35,
    'rgb(255, 255, 153)': 36,
    'rgb(153, 204, 255)': 37,
    'rgb(255, 153, 204)': 38,
    'rgb(204, 153, 255)': 39,
    'rgb(255, 204, 153)': 40,
    'rgb(51, 102, 255)': 41,
    'rgb(51, 204, 204)': 42,
    'rgb(153, 204, 0)': 43,
    'rgb(255, 204, 0)': 44,
    'rgb(255, 153, 0)': 45,
    'rgb(255, 102, 0)': 46,
    'rgb(102, 102, 153)': 47,
    'rgb(150, 150, 150)': 48,
    'rgb(0, 51, 102)': 49,
    'rgb(51, 153, 102)': 50,
    'rgb(0, 51, 0)': 51,
    'rgb(51, 51, 0)': 52,
    'rgb(153, 51, 0)': 53,
    'rgb(153, 51, 102)': 54,
    'rgb(51, 51, 153)': 55,
    'rgb(51, 51, 51)': 56
}


def css2excel(css):
    xf_list = []
    fnt = Font()
    borders = Borders()
    pattern = Pattern()
    align = Alignment()

    process_css = {
        'font-family': [fnt, "name", lambda x: x.split(",")[0]],
        'color': [fnt, "colour_index", lambda x: excel_color_map.get(x, 0)+8],
        'font-weight': [fnt, "bold", lambda x: x == 'bold'],
        'font-style': [fnt, "italic", lambda x: x == 'italic'],
        'text-align': [align, "horz",
                       lambda x: {'left': align.HORZ_LEFT,
                                  'right': align.HORZ_RIGHT,
                                  'center': align.HORZ_CENTER,
                                  'justified': align.HORZ_JUSTIFIED}[x]],
        'vertical-align': [align, "horz",
                           lambda x: {'top': 'top',
                                      'middle': 'center',
                                      'bottom': 'bottom',
                                      'justify': align.HORZ_JUSTIFIED}[x]],
        'background-color': [pattern, "pattern_fore_colour",
                             lambda x: excel_color_map.get(x, -7)+8],
    }
    for i in css.keys():
        if i in process_css.keys():
            setattr(process_css[i][0],
                    process_css[i][1],
                    process_css[i][2](css[i]))

    style = XFStyle()
    style.font = fnt
    borders.left = Borders.THIN
    borders.right = Borders.THIN
    borders.top = Borders.THIN
    borders.bottom = Borders.THIN
    style.borders = borders
    style.pattern = pattern
    style.pattern.pattern = 1
    style.alignment = align

    return style
