# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://www.vauxoo.com>).
#    All Rights Reserved
# #############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from xlwt import XFStyle, Borders, Pattern, Font, Alignment

WEB_COLORS = {
    "Aliceblue": "#F0F8FF",
    "Antiquewhite": "#FAEBD7",
    "Aqua": "#00FFFF",
    "Aquamarine": "#7FFFD4",
    "Azure": "#F0FFFF",
    "Beige": "#F5F5DC",
    "Bisque": "#FFE4C4",
    "Black": "#000000",
    "Blanchedalmond": "#FFEBCD",
    "Blue": "#0000FF",
    "Blueviolet": "#8A2BE2",
    "Brown": "#A52A2A",
    "Burlywood": "#DEB887",
    "Cadetblue": "#5F9EA0",
    "Chartreuse": "#7FFF00",
    "Chocolate": "#D2691E",
    "Coral": "#FF7F50",
    "Cornflowerblue": "#6495ED",
    "Cornsilk": "#FFF8DC",
    "Crimson": "#DC143C",
    "Cyan": "#00FFFF",
    "Darkblue": "#00008B",
    "Darkcyan": "#008B8B",
    "Darkgoldenrod": "#B8860B",
    "Darkgray": "#A9A9A9",
    "Darkgrey": "#A9A9A9",
    "Darkgreen": "#006400",
    "Darkkhaki": "#BDB76B",
    "Darkmagenta": "#8B008B",
    "Darkolivegreen": "#556B2F",
    "Darkorange": "#FF8C00",
    "Darkorchid": "#9932CC",
    "Darkred": "#8B0000",
    "Darksalmon": "#E9967A",
    "Darkseagreen": "#8FBC8F",
    "Darkslateblue": "#483D8B",
    "Darkslategray": "#2F4F4F",
    "Darkslategrey": "#2F4F4F",
    "Darkturquoise": "#00CED1",
    "Darkviolet": "#9400D3",
    "Deeppink": "#FF1493",
    "Deepskyblue": "#00BFFF",
    "Dimgray": "#696969",
    "Dimgrey": "#696969",
    "Dodgerblue": "#1E90FF",
    "Firebrick": "#B22222",
    "Floralwhite": "#FFFAF0",
    "Forestgreen": "#228B22",
    "Fuchsia": "#FF00FF",
    "Gainsboro": "#DCDCDC",
    "Ghostwhite": "#F8F8FF",
    "Gold": "#FFD700",
    "Goldenrod": "#DAA520",
    "Gray": "#808080",
    "Grey": "#808080",
    "Green": "#008000",
    "Greenyellow": "#ADFF2F",
    "Honeydew": "#F0FFF0",
    "Hotpink": "#FF69B4",
    "Indianred": "#CD5C5C",
    "Indigo": "#4B0082",
    "Ivory": "#FFFFF0",
    "Khaki": "#F0E68C",
    "Lavender": "#E6E6FA",
    "Lavenderblush": "#FFF0F5",
    "Lawngreen": "#7CFC00",
    "Lemonchiffon": "#FFFACD",
    "Lightblue": "#ADD8E6",
    "Lightcoral": "#F08080",
    "Lightcyan": "#E0FFFF",
    "Lightgoldenrodyellow": "#FAFAD2",
    "Lightgray": "#D3D3D3",
    "Lightgrey": "#D3D3D3",
    "Lightgreen": "#90EE90",
    "Lightpink": "#FFB6C1",
    "Lightsalmon": "#FFA07A",
    "Lightseagreen": "#20B2AA",
    "Lightskyblue": "#87CEFA",
    "Lightslategray": "#778899",
    "Lightslategrey": "#778899",
    "Lightsteelblue": "#B0C4DE",
    "Lightyellow": "#FFFFE0",
    "Lime": "#00FF00",
    "Limegreen": "#32CD32",
    "Linen": "#FAF0E6",
    "Magenta": "#FF00FF",
    "Maroon": "#800000",
    "Mediumaquamarine": "#66CDAA",
    "Mediumblue": "#0000CD",
    "Mediumorchid": "#BA55D3",
    "Mediumpurple": "#9370D8",
    "Mediumseagreen": "#3CB371",
    "Mediumslateblue": "#7B68EE",
    "Mediumspringgreen": "#00FA9A",
    "Mediumturquoise": "#48D1CC",
    "Mediumvioletred": "#C71585",
    "Midnightblue": "#191970",
    "Mintcream": "#F5FFFA",
    "Mistyrose": "#FFE4E1",
    "Moccasin": "#FFE4B5",
    "Navajowhite": "#FFDEAD",
    "Navy": "#000080",
    "Oldlace": "#FDF5E6",
    "Olive": "#808000",
    "Olivedrab": "#6B8E23",
    "Orange": "#FFA500",
    "Orangered": "#FF4500",
    "Orchid": "#DA70D6",
    "Palegoldenrod": "#EEE8AA",
    "Palegreen": "#98FB98",
    "Paleturquoise": "#AFEEEE",
    "Palevioletred": "#D87093",
    "Papayawhip": "#FFEFD5",
    "Peachpuff": "#FFDAB9",
    "Peru": "#CD853F",
    "Pink": "#FFC0CB",
    "Plum": "#DDA0DD",
    "Powderblue": "#B0E0E6",
    "Purple": "#800080",
    "Red": "#FF0000",
    "Rosybrown": "#BC8F8F",
    "Royalblue": "#4169E1",
    "Saddlebrown": "#8B4513",
    "Salmon": "#FA8072",
    "Sandybrown": "#F4A460",
    "Seagreen": "#2E8B57",
    "Seashell": "#FFF5EE",
    "Sienna": "#A0522D",
    "Silver": "#C0C0C0",
    "Skyblue": "#87CEEB",
    "Slateblue": "#6A5ACD",
    "Slategray": "#708090",
    "Slategrey": "#708090",
    "Snow": "#FFFAFA",
    "Springgreen": "#00FF7F",
    "Steelblue": "#4682B4",
    "Tan": "#D2B48C",
    "Teal": "#008080",
    "Thistle": "#D8BFD8",
    "Tomato": "#FF6347",
    "Turquoise": "#40E0D0",
    "Violet": "#EE82EE",
    "Wheat": "#F5DEB3",
    "White": "#FFFFFF",
    "Whitesmoke": "#F5F5F5",
    "Yellow": "#FFFF00",
    "Yellowgreen": "#9ACD32"
}

# Culled from a table at http://www.mvps.org/dmcritchie/excel/colors.htm
XLWT_COLORS = [
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (128, 0, 0),
    (0, 128, 0),
    (0, 0, 128),
    (128, 128, 0),
    (128, 0, 128),
    (0, 128, 128),
    (192, 192, 192),
    (128, 128, 128),
    (153, 153, 255),
    (153, 51, 102),
    (255, 255, 204),
    (204, 255, 255),
    (102, 0, 102),
    (255, 128, 128),
    (0, 102, 204),
    (204, 204, 255),
    (0, 0, 128),
    (255, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (128, 0, 128),
    (128, 0, 0),
    (0, 128, 128),
    (0, 0, 255),
    (0, 204, 255),
    (204, 255, 255),
    (204, 255, 204),
    (255, 255, 153),
    (153, 204, 255),
    (255, 153, 204),
    (204, 153, 255),
    (255, 204, 153),
    (51, 102, 255),
    (51, 204, 204),
    (153, 204, 0),
    (255, 204, 0),
    (255, 153, 0),
    (255, 102, 0),
    (102, 102, 153),
    (150, 150, 150),
    (0, 51, 102),
    (51, 153, 102),
    (0, 51, 0),
    (51, 51, 0),
    (153, 51, 0),
    (153, 51, 102),
    (51, 51, 153),
    (51, 51, 51)
]


def color_distance(rgb1, rgb2):
    # Adapted from Colour metric by Thiadmer Riemersma,
    # http://www.compuphase.com/cmetric.htm
    rmean = (rgb1[0] + rgb2[0]) / 2
    rgbr = rgb1[0] - rgb2[0]
    rgbg = rgb1[1] - rgb2[1]
    rgbb = rgb1[2] - rgb2[2]
    distance = (((512 + rmean) * rgbr * rgbr) / 256)
    distance += 4 * rgbg * rgbg
    distance += (((767 - rmean) * rgbb * rgbb) / 256)
    return distance


def htmlcolortorgb(colorstring):
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#':
        colorstring = colorstring[1:]
    else:
        if colorstring.title() in WEB_COLORS:
            colorstring = WEB_COLORS[colorstring.title()][1:]
    # Update color code from #FFF to #FFFFFF
    if len(colorstring) == 3:
        colorstring = ''.join([colorstring[0], colorstring[0], colorstring[1],
                               colorstring[1], colorstring[2], colorstring[2]])

    (rgbr, rgbg, rgbb) = (0, 0, 0)
    if len(colorstring) == 6:
        rgbr, rgbg, rgbb = colorstring[:2], colorstring[2:4], colorstring[4:]
        rgbr, rgbg, rgbb = [int(n, 16) for n in (rgbr, rgbg, rgbb)]
    return (rgbr, rgbg, rgbb)


def match_color_index(color):
    """Takes an "R,G,B" string or wx.Color and returns a matching xlwt
    color.
    """
    color = htmlcolortorgb(color)
    if isinstance(color, int):
        return color
    if color:
        distances = [color_distance(color, x) for x in XLWT_COLORS]
        result = distances.index(min(distances))
    return result


def get_font_height(height):
    size = 10
    factor = 1
    if height[-2:] == 'EM':
        factor = float(height[:-2])
    elif height[-2:] == 'PT':
        size = int(height[:-2])
    elif height[-2:] == 'PX':
        factor = float(height[:-2])/16
    elif height[-1:] == '%':
        factor = float(height[:-1])/100
    elif height == 'XX-SMALL':
        factor = 0.6
    elif height == 'X-SMALL':
        factor = 0.75
    elif height == 'SMALL':
        factor = 0.89
    elif height == 'MEDIUM':
        factor = 1
    elif height == 'LARGE':
        factor = 1.2
    elif height == 'X-LARGE':
        factor = 1.5
    elif height == 'XX-LARGE':
        factor = 2
    new_size = float(size * factor * 20)
    return new_size


def get_horizontal_align(halign, align):
    if halign:
        halign = halign.strip().upper()
    style = {
        'LEFT': align.HORZ_LEFT,
        'RIGHT': align.HORZ_RIGHT,
        'CENTER': align.HORZ_CENTER,
        'JUSTIFY': align.HORZ_JUSTIFIED
    }
    new_halign = align.HORZ_GENERAL
    if halign in style.keys():
        new_halign = style[halign]
    return new_halign


def get_vertical_align(valign, align):
    if valign:
        valign = valign.strip().upper()
    style = {
        'TOP': align.VERT_TOP,
        'MIDDLE': align.VERT_CENTER,
        'BOTTOM': align.VERT_BOTTOM,
        'JUSTIFY': align.VERT_JUSTIFIED
    }
    new_valign = align.VERT_TOP
    if valign in style.keys():
        new_valign = style[valign]
    return new_valign


def css2excel(css):
    fnt = Font()
    borders = Borders()
    pattern = Pattern()
    align = Alignment()

    process_css = {
        'font-family': [fnt, "name", lambda x: x.split(",")[0]],
        'font-size': [fnt, "height", lambda x: get_font_height(x.upper())],
        'color': [fnt, "colour_index", lambda x: match_color_index(x.upper())],
        'font-weight': [fnt, "bold", lambda x: x == 'bold'],
        'font-style': [fnt, "italic", lambda x: x == 'italic'],
        'text-align': [align, "horz",
                       lambda x: get_horizontal_align(x, align)],
        'vertical-align': [align, "vert",
                           lambda x: get_vertical_align(x, align)],
        'background-color': [pattern, "pattern_fore_colour",
                             lambda x: match_color_index(x.upper())],
    }
    for i in css.keys():
        if i in process_css.keys():
            setattr(process_css[i][0],
                    process_css[i][1],
                    process_css[i][2](css[i].strip()))

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
