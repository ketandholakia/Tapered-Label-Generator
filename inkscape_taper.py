import math
import inkex
from inkex import PathElement, Path

class ConicalLabel(inkex.GenerateExtension):
    def add_arguments(self, pars):
        pars.add_argument("--top_diameter", type=float, default=40.0, help="Top diameter (mm)")
        pars.add_argument("--bottom_diameter", type=float, default=70.0, help="Bottom diameter (mm)")
        pars.add_argument("--height", type=float, default=100.0, help="Label height (mm)")

    def effect(self):
        top_r = self.options.top_diameter / 2
        bottom_r = self.options.bottom_diameter / 2
        height = self.options.height

        slant = math.sqrt((bottom_r - top_r)**2 + height**2)
        angle = 360 * (bottom_r - top_r) / slant

        # Calculate arc endpoints
        end_angle = math.radians(angle)
        x1 = bottom_r * math.sin(end_angle)
        y1 = -bottom_r * math.cos(end_angle)
        x2 = top_r * math.sin(end_angle)
        y2 = -top_r * math.cos(end_angle)

        large_arc = 1 if angle > 180 else 0

        # Create path using SVG path string format
        path_str = f"M 0,0 A {bottom_r},{bottom_r} 0 {large_arc},1 {x1},{y1} L {x2},{y2} A {top_r},{top_r} 0 {large_arc},0 0,0 Z"
        path = Path(path_str)

        label = PathElement()
        label.path = path
        label.style = {"stroke": "#000000", "fill": "none"}
        self.svg.get_current_layer().add(label)

if __name__ == '__main__':
    ConicalLabel().run()