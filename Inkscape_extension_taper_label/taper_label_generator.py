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
        pars.add_argument("--corner_radius", type=float, default=3.0,
                         help="Radius for rounded corners in mm (0 = no rounding)")
        pars.add_argument("--surface_curvature_radius", type=float, default=0.0,
                         help="Surface curvature radius in mm (0 = flat surface, >0 = curved surface)")

    def validate_input(self, label_height, label_width, top_diameter, bottom_diameter, corner_radius, surface_curvature_radius):
        """Validate input parameters"""
        if label_height <= 0 or label_width <= 0:
            return False, "Label dimensions must be positive"
        if top_diameter <= 0 or bottom_diameter <= 0:
            return False, "Diameters must be positive"
        if corner_radius < 0:
            return False, "Corner radius must be non-negative"
        if corner_radius > min(label_height, label_width) / 2:
            return False, "Corner radius is too large for the label dimensions"
        if surface_curvature_radius < 0:
            return False, "Surface curvature radius must be non-negative"
        if surface_curvature_radius > 0 and surface_curvature_radius < min(top_diameter, bottom_diameter) / 4:
            return False, "Surface curvature radius is too small relative to the cone diameters"
        return True, ""

    def generate_rounded_rectangle(self, width, height, radius):
        """Generate SVG path for a rounded rectangle"""
        if radius <= 0:
            return f"M 0,0 L {width},0 L {width},{height} L 0,{height} Z"
        
        # Ensure radius doesn't exceed half of either dimension
        max_radius = min(width, height) / 2
        r = min(radius, max_radius)
        
        path_str = f"M {r},0"
        path_str += f" L {width-r},0"
        path_str += f" A {r},{r} 0 0,1 {width},{r}"
        path_str += f" L {width},{height-r}"
        path_str += f" A {r},{r} 0 0,1 {width-r},{height}"
        path_str += f" L {r},{height}"
        path_str += f" A {r},{r} 0 0,1 0,{height-r}"
        path_str += f" L 0,{r}"
        path_str += f" A {r},{r} 0 0,1 {r},0"
        path_str += " Z"
        
        return path_str

    def apply_surface_curvature(self, label_width, label_height, diameter, surface_curvature_radius):
        """Apply surface curvature adjustment to label dimensions"""
        if surface_curvature_radius <= 0:
            return label_width
        
        # Calculate the arc length adjustment for curved surface
        # For a curved surface, the label needs to be slightly wider to account for the curvature
        circumference = math.pi * diameter
        arc_angle = (label_width / circumference) * 2 * math.pi
        
        # Calculate the chord length vs arc length difference
        if arc_angle < math.pi:
            # For small angles, use arc length instead of chord length
            arc_length = surface_curvature_radius * arc_angle
            chord_length = 2 * surface_curvature_radius * math.sin(arc_angle / 2)
            curvature_factor = arc_length / chord_length if chord_length > 0 else 1.0
        else:
            curvature_factor = 1.0
        
        # Apply curvature adjustment
        adjusted_width = label_width * curvature_factor
        return adjusted_width

    def generate_conical_path(self, label_height, label_width, top_diameter, bottom_diameter, corner_radius, surface_curvature_radius):
        """Generate the SVG path for a conical label"""
        
        # Check if it's a cylindrical label (same diameters)
        if abs(top_diameter - bottom_diameter) < 0.001:
            # Apply surface curvature adjustment if specified
            adjusted_width = self.apply_surface_curvature(label_width, label_height, top_diameter, surface_curvature_radius)
            
            # Simple rectangle for cylindrical surface
            if corner_radius > 0:
                path_str = self.generate_rounded_rectangle(adjusted_width, label_height, corner_radius)
            else:
                path_str = f"M 0,0 L {adjusted_width},0 L {adjusted_width},{label_height} L 0,{label_height} Z"
            return path_str, adjusted_width, label_height, False
        
        # Conical label calculations
        j = top_diameter >= bottom_diameter
        u = max(top_diameter, bottom_diameter) / 2
        d = min(top_diameter, bottom_diameter) / 2
        p = u - d

        if p > label_height:
            raise ValueError("The difference between the two diameters is greater than the height of the label.")

        # Apply surface curvature adjustment to label width
        avg_diameter = (top_diameter + bottom_diameter) / 2
        adjusted_width = self.apply_surface_curvature(label_width, label_height, avg_diameter, surface_curvature_radius)

        _ = min(max(p / label_height, -1), 1)
        e = u / _
        n = d / _
        t = 2 * adjusted_width / (e + n)
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
        
        if corner_radius > 0:
            # Generate rounded conical path
            path_str = self.generate_rounded_conical_path(
                E, k, D, S, T, z, M, F, e, n, g, corner_radius
            )
        else:
            # Original sharp-cornered path
            path_str = f"M {E:.3f},{k:.3f} L {D:.3f},{S:.3f}"
            path_str += f" A {e:.3f},{e:.3f} 0 {g},0 {T:.3f},{z:.3f}"
            path_str += f" L {M:.3f},{F:.3f}"
            path_str += f" A {n:.3f},{n:.3f} 0 {g},1 {E:.3f},{k:.3f}"
            path_str += " Z"

        return path_str, a, r, j

    def generate_rounded_conical_path(self, E, k, D, S, T, z, M, F, e, n, g, corner_radius):
        """Generate SVG path for a rounded conical label"""
        # For conical shapes, we'll add small rounded corners at the four main vertices
        # This is a simplified approach - for more complex shapes, more sophisticated
        # corner rounding would be needed
        
        # Calculate the distances and angles for corner rounding
        r = min(corner_radius, 5.0)  # Limit corner radius for conical shapes
        
        # Calculate corner points with offsets for rounding
        # These calculations are approximations for the complex conical geometry
        
        # Start point with rounded corner
        start_x = E + r * 0.1
        start_y = k + r * 0.1
        
        path_str = f"M {start_x:.3f},{start_y:.3f}"
        
        # Add rounded corners at each vertex
        # Corner 1: From E,k to D,S
        path_str += f" L {D-r*0.1:.3f},{S-r*0.1:.3f}"
        path_str += f" Q {D:.3f},{S:.3f} {D+r*0.1:.3f},{S+r*0.1:.3f}"
        
        # Large arc (unchanged)
        path_str += f" A {e:.3f},{e:.3f} 0 {g},0 {T-r*0.1:.3f},{z+r*0.1:.3f}"
        
        # Corner 2: At T,z
        path_str += f" Q {T:.3f},{z:.3f} {T+r*0.1:.3f},{z-r*0.1:.3f}"
        
        # Line to next corner
        path_str += f" L {M+r*0.1:.3f},{F-r*0.1:.3f}"
        
        # Corner 3: At M,F
        path_str += f" Q {M:.3f},{F:.3f} {M-r*0.1:.3f},{F+r*0.1:.3f}"
        
        # Second large arc (unchanged)
        path_str += f" A {n:.3f},{n:.3f} 0 {g},1 {E+r*0.1:.3f},{k+r*0.1:.3f}"
        
        # Corner 4: Back to start
        path_str += f" Q {E:.3f},{k:.3f} {start_x:.3f},{start_y:.3f}"
        
        path_str += " Z"
        
        return path_str

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
        corner_radius = self.options.corner_radius
        surface_curvature_radius = self.options.surface_curvature_radius

        # Validate input
        is_valid, error_msg = self.validate_input(label_height, label_width, top_diameter, bottom_diameter, corner_radius, surface_curvature_radius)
        if not is_valid:
            inkex.errormsg(f"Input Error: {error_msg}")
            return

        try:
            # Generate the path
            path_data, width, height, is_inverted = self.generate_conical_path(
                label_height, label_width, top_diameter, bottom_diameter, corner_radius, surface_curvature_radius
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
                                      top_diameter, bottom_diameter, width, height, corner_radius, surface_curvature_radius)
            
            # Add to document
            self.svg.get_current_layer().append(group)
            
        except ValueError as e:
            inkex.errormsg(f"Calculation Error: {str(e)}")
        except Exception as e:
            inkex.errormsg(f"Unexpected Error: {str(e)}")

    def add_dimension_text(self, group, label_height, label_width, top_diameter, 
                          bottom_diameter, width, height, corner_radius, surface_curvature_radius):
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
        if corner_radius > 0:
            text1.text = f"Taper Label: {label_height} x {label_width}mm (r={corner_radius}mm)"
        else:
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
        
        # Corner radius information (if applicable)
        text_line = 2
        if corner_radius > 0:
            text3 = TextElement()
            text3.text = f"Corner Radius: {corner_radius}mm"
            text3.set('x', str(text_x))
            text3.set('y', str(text_y + text_line * line_height))
            text3.style = {
                'font-family': 'Arial, sans-serif',
                'font-size': f'{font_size}px',
                'font-weight': 'bold',
                'fill': 'black'
            }
            text_group.append(text3)
            text_line += 1
        
        # Surface curvature radius information (if applicable)
        if surface_curvature_radius > 0:
            text4 = TextElement()
            text4.text = f"Surface Curvature: {surface_curvature_radius}mm radius"
            text4.set('x', str(text_x))
            text4.set('y', str(text_y + text_line * line_height))
            text4.style = {
                'font-family': 'Arial, sans-serif',
                'font-size': f'{font_size}px',
                'font-weight': 'bold',
                'fill': 'black'
            }
            text_group.append(text4)
        
        group.append(text_group)


if __name__ == '__main__':
    TaperedLabelGenerator().run()