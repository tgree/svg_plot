# Copyright (c) 2020 by Terry Greeniaus.
from .svg_renderer import SVGRenderer
from .ticker_extended import gen_ticks_extended


class ExtentMapper:
    def __init__(self, d_min, d_max, plot_min, plot_max):
        self.d_min    = d_min
        self.d_max    = d_max
        self.plot_min = plot_min
        self.plot_max = plot_max
        self.ratio    = (plot_max - plot_min) / (d_max - d_min)

    def __call__(self, v):
        return (v - self.d_min) * self.ratio


class Point:
    def __init__(self, x, y, r=1, color=0x1F77B4, attrs=None):
        self.x     = x
        self.y     = y
        self.r     = r
        self.color = color
        self.attrs = attrs or {}


class Plot:
    def __init__(self, points, flip_x_axis=False, x_legend='', y_legend=''):
        self.points      = points
        self.flip_x_axis = flip_x_axis
        self.x_legend    = x_legend
        self.y_legend    = y_legend

    @staticmethod
    def from_tuples(tuples, tuple_attrs=None, **kwargs):
        if not tuple_attrs:
            return Plot([Point(*t) for t in tuples], **kwargs)

        return Plot([Point(*t, attrs=ta) for t, ta in zip(tuples, tuple_attrs)],
                    **kwargs)

    def render(self, pixel_width=593, pixel_height=415, include_x_zero=False,
               include_y_zero=False, x_fmt=None, y_fmt=None):
        margin_l = 80
        margin_r = 16
        margin_t = 16
        margin_b = pixel_height // 8

        plot_width  = pixel_width - margin_l - margin_r
        plot_height = pixel_height - margin_t - margin_b

        sr = SVGRenderer(pixel_width, pixel_height)
        sr.add_rect(margin_l, margin_t, plot_width, plot_height)

        min_x = min(p.x for p in self.points)
        max_x = max(p.x for p in self.points)
        if include_x_zero:
            min_x = min(min_x, 0)
            max_x = max(max_x, 0)
        x_margin = (max_x - min_x) * 0.05
        x_ticks  = gen_ticks_extended(min_x - x_margin, max_x + x_margin, m=8)
        if self.flip_x_axis:
            x_map = ExtentMapper(x_ticks.d_max, x_ticks.d_min,
                                 margin_l, pixel_width - margin_r)
        else:
            x_map = ExtentMapper(x_ticks.d_min, x_ticks.d_max,
                                 margin_l, pixel_width - margin_r)

        min_y = min(p.y for p in self.points)
        max_y = max(p.y for p in self.points)
        if include_y_zero:
            min_y = min(min_y, 0)
            max_y = max(max_y, 0)
        y_margin = (max_y - min_y) * 0.05
        y_ticks = gen_ticks_extended(min_y - y_margin, max_y + y_margin, m=5)
        y_map   = ExtentMapper(y_ticks.d_max, y_ticks.d_min,
                               margin_t, pixel_height - margin_b)

        for p in self.points:
            sr.add_circle(margin_l + x_map(p.x), margin_t + y_map(p.y),
                          max(p.r, 1),
                          style=("fill:#%x;stroke:transparent;" % p.color),
                          **p.attrs)

        for l, t in zip(x_ticks.get_d_locs(), x_ticks.get_d_labels(fmt=x_fmt)):
            lx = x_map(l)
            sr.add_line(margin_l + lx, pixel_height - margin_b,
                        margin_l + lx, pixel_height - margin_b + 8)
            sr.add_text(margin_l + lx, pixel_height - margin_b + 20, t,
                        textAnchor="middle", fontFamily="sans-serif",
                        fontSize="14px")

        for l, t in zip(y_ticks.get_d_locs(), y_ticks.get_d_labels(fmt=y_fmt)):
            ly = y_map(l)
            sr.add_line(margin_l - 8, margin_t + ly,
                        margin_l - 0, margin_t + ly)
            sr.add_text(margin_l - 10, margin_t + ly + 4, t, textAnchor="end",
                        fontFamily="sans-serif", fontSize="14px")

        sr.add_text(margin_l + plot_width / 2, pixel_height - margin_b + 36,
                    self.x_legend, textAnchor="middle", fontFamily="sans-serif",
                    fontSize="14px")
        tx = 16
        ty = margin_t + plot_height / 2
        sr.add_text(tx, ty, self.y_legend,
                    textAnchor="middle", fontFamily="sans-serif",
                    fontSize="14px",
                    transform="rotate(270, %s, %s)" % (tx, ty))

        return sr.render_xml()
