import math
import svgwrite

def generate_conical_label(top_dia, bottom_dia, height, filename='conical_label.svg'):
    # Convert diameters to radii
    r1 = top_dia / 2
    r2 = bottom_dia / 2

    # Slant height of the frustum sides
    l = math.sqrt((r2 - r1)**2 + height**2)

    # Arc lengths (circumference of top and bottom circles)
    arc_top = 2 * math.pi * r1
    arc_bottom = 2 * math.pi * r2

    # Angles for the arcs (in radians)
    angle_top = arc_top / l
    angle_bottom = arc_bottom / l

    # Convert to degrees
    angle_deg = math.degrees(angle_bottom)

    # Create SVG drawing
    dwg = svgwrite.Drawing(filename, size=('1000px', '1000px'))
    center = (500, 500)

    # Points on the arc
    def polar_to_cartesian(r, angle_rad):
        return (
            center[0] + r * math.cos(angle_rad),
            center[1] + r * math.sin(angle_rad)
        )

    # Start and end angles
    start_angle = -angle_bottom / 2
    end_angle = angle_bottom / 2

    # Points
    p1 = polar_to_cartesian(r2, start_angle)
    p2 = polar_to_cartesian(r1, start_angle)
    p3 = polar_to_cartesian(r1, end_angle)
    p4 = polar_to_cartesian(r2, end_angle)

    # Path for the conical label
    path = dwg.path(d=f"M {p1[0]},{p1[1]}", fill='lightblue', stroke='black', stroke_width=1)
    path.push(f"L {p2[0]},{p2[1]}")
    path.push_arc(p3, 0, r=r1, large_arc=False, angle_dir='+')
    path.push(f"L {p4[0]},{p4[1]}")
    path.push_arc(p1, 0, r=r2, large_arc=False, angle_dir='-')
    path.push("Z")

    dwg.add(path)
    dwg.save()
    print(f"SVG saved as {filename}")

# Example usage
generate_conical_label(top_dia=30, bottom_dia=60, height=100)