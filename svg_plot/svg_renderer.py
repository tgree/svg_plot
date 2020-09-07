# Copyright (c) 2020 by Terry Greeniaus.
import re
import html


class SVGElem:
    def __init__(self, **attrs):
        self.xml = ''
        for k, v in attrs.items():
            k         = re.sub(r'(?<!^)(?=[A-Z])', '-', k).lower()
            self.xml += ' %s="%s"' % (k, html.escape(v))


class SVGRect(SVGElem):
    def __init__(self, x, y, width, height, **attrs):
        super(SVGRect, self).__init__(**attrs)
        self.xml = ('<rect x="%s" y="%s" width="%s" height="%s"' %
                    (x, y, width, height)) + self.xml + '/>'


class SVGLine(SVGElem):
    def __init__(self, x1, y1, x2, y2, **attrs):
        super(SVGLine, self).__init__(**attrs)
        self.xml = ('<line x1="%s" y1="%s" x2="%s" y2="%s"' %
                    (x1, y1, x2, y2)) + self.xml + '/>'


class SVGCircle(SVGElem):
    def __init__(self, cx, cy, r, **attrs):
        super(SVGCircle, self).__init__(**attrs)
        self.xml = ('<circle cx="%s" cy="%s" r="%s"' %
                    (cx, cy, r)) + self.xml + '/>'


class SVGText(SVGElem):
    def __init__(self, x, y, text, **attrs):
        super(SVGText, self).__init__(**attrs)
        self.xml = ('<text x="%s" y="%s"' %
                    (x, y)) + self.xml + ('>%s</text>' % text)


class SVGRenderer:
    '''
    Class that allows you to build an SVG in XML format by adding primitives to
    a blank document.
    '''
    def __init__(self, width, height, view_box=None):
        self.width    = width
        self.height   = height
        self.view_box = view_box or (0, 0, width, height)
        self.elements = []

    def add_rect(self, x, y, width, height,
                 style="fill:transparent;stroke:black;stroke-width:1",
                 **attrs):
        '''
        Adds a rectangle element to the document.
        '''
        self.elements.append(SVGRect(x, y, width, height, style=style, **attrs))

    def add_circle(self, cx, cy, r, style="fill:black;stroke:transparent",
                   **attrs):
        '''
        Adds a circle element to the document.
        '''
        self.elements.append(SVGCircle(cx, cy, r, style=style, **attrs))

    def add_line(self, x1, y1, x2, y2, style="fill:transparent;stroke:black",
                 **attrs):
        '''
        Adds a line element to the document.
        '''
        self.elements.append(SVGLine(x1, y1, x2, y2, style=style, **attrs))

    def add_text(self, x, y, text, **attrs):
        '''
        Adds a text element to the document.
        '''
        self.elements.append(SVGText(x, y, text, **attrs))

    def render_xml(self):
        '''
        Returns an XML representation of the document as a string.
        '''
        xml  = '<?xml version="1.0" encoding="utf-8" standalone="no"?>\n'
        xml += ('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
                '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
        xml += ('<svg width="%spx" height="%spx" viewBox="%s %s %s %s" '
                'version="1.1" xmlns="http://www.w3.org/2000/svg" '
                'xmlns:xlink="http://www.w3.org/1999/xlink">\n' %
                (self.width, self.height, *self.view_box))

        for e in self.elements:
            xml += '%s\n' % e.xml

        xml += '</svg>'

        return xml
