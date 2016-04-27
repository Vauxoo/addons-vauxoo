# -*- coding: utf-8 -*-

from xlwt import XFStyle, Borders, Pattern, Font, Alignment

WEB_COLORS = {
    "AliceBlue": "#F0F8FF",
    "AntiqueWhite": "#FAEBD7",
    "Aqua": "#00FFFF",
    "Aquamarine": "#7FFFD4",
    "Azure": "#F0FFFF",
    "Beige": "#F5F5DC",
    "Bisque": "#FFE4C4",
    "Black": "#000000",
    "BlanchedAlmond": "#FFEBCD",
    "Blue": "#0000FF",
    "BlueViolet": "#8A2BE2",
    "Brown": "#A52A2A",
    "BurlyWood": "#DEB887",
    "CadetBlue": "#5F9EA0",
    "Chartreuse": "#7FFF00",
    "Chocolate": "#D2691E",
    "Coral": "#FF7F50",
    "CornflowerBlue": "#6495ED",
    "Cornsilk": "#FFF8DC",
    "Crimson": "#DC143C",
    "Cyan": "#00FFFF",
    "DarkBlue": "#00008B",
    "DarkCyan": "#008B8B",
    "DarkGoldenRod": "#B8860B",
    "DarkGray": "#A9A9A9",
    "DarkGrey": "#A9A9A9",
    "DarkGreen": "#006400",
    "DarkKhaki": "#BDB76B",
    "DarkMagenta": "#8B008B",
    "DarkOliveGreen": "#556B2F",
    "Darkorange": "#FF8C00",
    "DarkOrchid": "#9932CC",
    "DarkRed": "#8B0000",
    "DarkSalmon": "#E9967A",
    "DarkSeaGreen": "#8FBC8F",
    "DarkSlateBlue": "#483D8B",
    "DarkSlateGray": "#2F4F4F",
    "DarkSlateGrey": "#2F4F4F",
    "DarkTurquoise": "#00CED1",
    "DarkViolet": "#9400D3",
    "DeepPink": "#FF1493",
    "DeepSkyBlue": "#00BFFF",
    "DimGray": "#696969",
    "DimGrey": "#696969",
    "DodgerBlue": "#1E90FF",
    "FireBrick": "#B22222",
    "FloralWhite": "#FFFAF0",
    "ForestGreen": "#228B22",
    "Fuchsia": "#FF00FF",
    "Gainsboro": "#DCDCDC",
    "GhostWhite": "#F8F8FF",
    "Gold": "#FFD700",
    "GoldenRod": "#DAA520",
    "Gray": "#808080",
    "Grey": "#808080",
    "Green": "#008000",
    "GreenYellow": "#ADFF2F",
    "HoneyDew": "#F0FFF0",
    "HotPink": "#FF69B4",
    "IndianRed": "#CD5C5C",
    "Indigo": "#4B0082",
    "Ivory": "#FFFFF0",
    "Khaki": "#F0E68C",
    "Lavender": "#E6E6FA",
    "LavenderBlush": "#FFF0F5",
    "LawnGreen": "#7CFC00",
    "LemonChiffon": "#FFFACD",
    "LightBlue": "#ADD8E6",
    "LightCoral": "#F08080",
    "LightCyan": "#E0FFFF",
    "LightGoldenRodYellow": "#FAFAD2",
    "LightGray": "#D3D3D3",
    "LightGrey": "#D3D3D3",
    "LightGreen": "#90EE90",
    "LightPink": "#FFB6C1",
    "LightSalmon": "#FFA07A",
    "LightSeaGreen": "#20B2AA",
    "LightSkyBlue": "#87CEFA",
    "LightSlateGray": "#778899",
    "LightSlateGrey": "#778899",
    "LightSteelBlue": "#B0C4DE",
    "LightYellow": "#FFFFE0",
    "Lime": "#00FF00",
    "LimeGreen": "#32CD32",
    "Linen": "#FAF0E6",
    "Magenta": "#FF00FF",
    "Maroon": "#800000",
    "MediumAquaMarine": "#66CDAA",
    "MediumBlue": "#0000CD",
    "MediumOrchid": "#BA55D3",
    "MediumPurple": "#9370D8",
    "MediumSeaGreen": "#3CB371",
    "MediumSlateBlue": "#7B68EE",
    "MediumSpringGreen": "#00FA9A",
    "MediumTurquoise": "#48D1CC",
    "MediumVioletRed": "#C71585",
    "MidnightBlue": "#191970",
    "MintCream": "#F5FFFA",
    "MistyRose": "#FFE4E1",
    "Moccasin": "#FFE4B5",
    "NavajoWhite": "#FFDEAD",
    "Navy": "#000080",
    "OldLace": "#FDF5E6",
    "Olive": "#808000",
    "OliveDrab": "#6B8E23",
    "Orange": "#FFA500",
    "OrangeRed": "#FF4500",
    "Orchid": "#DA70D6",
    "PaleGoldenRod": "#EEE8AA",
    "PaleGreen": "#98FB98",
    "PaleTurquoise": "#AFEEEE",
    "PaleVioletRed": "#D87093",
    "PapayaWhip": "#FFEFD5",
    "PeachPuff": "#FFDAB9",
    "Peru": "#CD853F",
    "Pink": "#FFC0CB",
    "Plum": "#DDA0DD",
    "PowderBlue": "#B0E0E6",
    "Purple": "#800080",
    "Red": "#FF0000",
    "RosyBrown": "#BC8F8F",
    "RoyalBlue": "#4169E1",
    "SaddleBrown": "#8B4513",
    "Salmon": "#FA8072",
    "SandyBrown": "#F4A460",
    "SeaGreen": "#2E8B57",
    "SeaShell": "#FFF5EE",
    "Sienna": "#A0522D",
    "Silver": "#C0C0C0",
    "SkyBlue": "#87CEEB",
    "SlateBlue": "#6A5ACD",
    "SlateGray": "#708090",
    "SlateGrey": "#708090",
    "Snow": "#FFFAFA",
    "SpringGreen": "#00FF7F",
    "SteelBlue": "#4682B4",
    "Tan": "#D2B48C",
    "Teal": "#008080",
    "Thistle": "#D8BFD8",
    "Tomato": "#FF6347",
    "Turquoise": "#40E0D0",
    "Violet": "#EE82EE",
    "Wheat": "#F5DEB3",
    "White": "#FFFFFF",
    "WhiteSmoke": "#F5F5F5",
    "Yellow": "#FFFF00",
    "YellowGreen": "#9ACD32"
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
