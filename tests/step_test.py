# Copyright (c) 2020 by Terry Greeniaus.
from svg_plot import Plot


POINTS = [(1, 1, 10),
          (2, 2, 10),
          (3, 3, 10),
          (4, 4, 10),
          ]


print(Plot.from_tuples(POINTS).render(include_x_zero=True,
                                      include_y_zero=True))
