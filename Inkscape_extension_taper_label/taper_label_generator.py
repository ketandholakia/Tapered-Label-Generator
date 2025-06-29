#!/usr/bin/env python3
"""
Tapered Label Generator - Inkscape Extension
Based on viwtaper.py - generates conical/tapered labels for various surfaces
"""

import math
import inkex
from inkex import PathElement, TextElement, Group


class TaperedLabelGenerator(inkex.EffectExtension):
    """Extension to generate tapered labels for conical surfaces"""
    
    def add_arguments(self, pars):
        pars.add_argument("--label_height", type=float, default=100.0, 
                         help="Height of the label in mm")
        pars.add_argument("--label_width", type=float, default=50.0,
                         help="Width of the label in mm") 
        pars.add_argument("--top_diameter", type=float, default=80.0,
                         help="Top diameter of the cone in mm")
        pars.add_argument("--bottom_diameter", type=float, default=100.0,
                         help="Bottom diameter of the cone in mm")
        pars.add_argument("--add_dimensions", type=inkex.Boolean, default=True,
                         help="Add dimension text to the label")
        pars.add_argument("--stroke_width", type=float, default=0.15,
                         help="Stroke width for the path")
        pars.add_argument("--fill_color", type=str, default="#C4E9FB",
                         help="Fill color for the label")
        pars.add_argument("--stroke_color", type=str, default="#000000", 
                         help="Stroke color for the label")

    def validate_input(self, label_height, label_width, top_diameter, bottom_diameter):
        """Validate input parameters"""
        if label_height <= 0 or label_width <= 0:
            return False, "Label dimensions must be positive"
        if top_diameter <= 0 or bottom_diameter <= 0:
            return False, "Diameters must be positive"
        return True, ""

    def generate_conical_path(self, label_height, label_width, top_diameter, bottom_diameter):
        """Generate the SVG path for a conical label"""
        
        # Check if it's a cylindrical label (same diameters)
        if abs(top_diameter - bottom_diameter) < 0.001:
            # Simple rectangle for cylindrical surface
            path_str = f"M 0,0 L {label_width},0 L {label_width},{label_height} L 0,{label_height} Z"
            return path_str, label_width, label_height, False
        
        # Conical label calculations
        j = top_diameter >= bottom_diameter
        u = max(top_diameter, bottom_diameter) / 2
        d = min(top_diameter, bottom_diameter) / 2
        p = u - d

        if p > label_height:
            raise ValueError("The difference between the two diameters is greater than the height of the label.")

        _ = min(max(p / label_height, -1), 1)
        e = u / _
        n = d / _
        t = 2 * label_width / (e + n)
        N = t * e
        A = t * n

        if N > math.pi * u * 2 or A > math.pi * d * 2:
            raise ValueError("The label will circle the surface more than once.")

        v = t > math.pi
        a = 2 * e * (1 if v else math.sin(t / 2))
        P = e * math.cos(t / 2)
        L = n * math.cos(t / 2)
        r = e - min(P, L)
        i = a / 2
        c = r - e
        w = math.sin(-t / 2)
        O = math.cos(-t / 2)
        x = math.sin(t / 2)
        C = math.cos(t / 2)
        E = i + w * n
        k = c + O * n
        D = i + w * e
        S = c + O * e
        M = i + x * n
        F = c + C * n
        T = i + x * e
        z = c + C * e
        g = 1 if v else 0
        
        path_str = f"M {E:.3f},{k:.3f} L {D:.3f},{S:.3f}"
        path_str += f" A {e:.3f},{e:.3f} 0 {g},0 {T:.3f},{z:.3f}"
        path_str += f" L {M:.3f},{F:.3f}"
        path_str += f" A {n:.3f},{n:.3f} 0 {g},1 {E:.3f},{k:.3f}"
        path_str += " Z"

        return path_str, a, r, j

    def effect(self):
        """Main effect method"""
        
        # Get parameters
        label_height = self.options.label_height
        label_width = self.options.label_width  
        top_diameter = self.options.top_diameter
        bottom_diameter = self.options.bottom_diameter
        add_dimensions = self.options.add_dimensions
        stroke_width = self.options.stroke_width
        fill_color = self.options.fill_color
        stroke_color = self.options.stroke_color

        # Validate input
        is_valid, error_msg = self.validate_input(label_height, label_width, top_diameter, bottom_diameter)
        if not is_valid:
            inkex.errormsg(f"Input Error: {error_msg}")
            return

        try:
            # Generate the path
            path_data, width, height, is_inverted = self.generate_conical_path(
                label_height, label_width, top_diameter, bottom_diameter
            )
            
            # Create a group to contain all elements
            group = Group()
            group.label = f"Tapered Label {label_height}x{label_width}mm"
            
            # Create the path element
            path_element = PathElement()
            path_element.path = path_data
            path_element.style = {
                'fill': fill_color,
                'stroke': stroke_color,
                'stroke-width': str(stroke_width),
                'stroke-linecap': 'round'
            }
            
            # Apply transform if needed for inverted labels
            if is_inverted:
                transform_str = f"translate(0, {height}) scale(1, -1)"
                path_element.transform = inkex.Transform(transform_str)
            
            group.append(path_element)
            
            # Add dimension text if requested
            if add_dimensions:
                self.add_dimension_text(group, label_height, label_width, 
                                      top_diameter, bottom_diameter, width, height)
            
            # Add to document
            self.svg.get_current_layer().append(group)
            
        except ValueError as e:
            inkex.errormsg(f"Calculation Error: {str(e)}")
        except Exception as e:
            inkex.errormsg(f"Unexpected Error: {str(e)}")

    def add_dimension_text(self, group, label_height, label_width, top_diameter, 
                          bottom_diameter, width, height):
        """Add dimension text to the label"""
        
        # Calculate text position and size
        margin = max(width, height) * 0.02
        font_size = max(width, height) * 0.03
        line_height = font_size * 1.2
        
        # Position text at the top-left
        text_x = margin
        text_y = margin + font_size
        
        # Create dimension text
        text_group = Group()
        text_group.label = "Dimensions"
        
        # Label dimensions text
        text1 = TextElement()
        text1.text = f"Taper Label: {label_height} x {label_width}mm"
        text1.set('x', str(text_x))
        text1.set('y', str(text_y))
        text1.style = {
            'font-family': 'Arial, sans-serif',
            'font-size': f'{font_size}px',
            'font-weight': 'bold',
            'fill': 'black'
        }
        text_group.append(text1)
        
        # Diameter information text
        text2 = TextElement()
        if abs(top_diameter - bottom_diameter) < 0.001:
            text2.text = f"Diameter: {top_diameter}mm (cylindrical)"
        else:
            text2.text = f"Diameters: {top_diameter}mm - {bottom_diameter}mm"
        
        text2.set('x', str(text_x))
        text2.set('y', str(text_y + line_height))
        text2.style = {
            'font-family': 'Arial, sans-serif',
            'font-size': f'{font_size}px',
            'font-weight': 'bold',
            'fill': 'black'
        }
        text_group.append(text2)
        
        group.append(text_group)


if __name__ == '__main__':
    TaperedLabelGenerator().run()