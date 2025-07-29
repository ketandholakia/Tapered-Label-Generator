import math
import tkinter as tk
import webbrowser
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from tkinter import filedialog
import tempfile
import os
from tkinter import ttk

def create_svg(width, height, viewBox, path, transform, label_height=None, label_width=None, top_diameter=None, bottom_diameter=None, overlap=False, overlap_amount=0, offset=0, offset_path=None):
    svg = Element('svg', {'version': "1.1", 'baseProfile': "tiny", 'xmlns': "http://www.w3.org/2000/svg", 'xmlns:xlink': "http://www.w3.org/1999/xlink"})
    svg.set('height', f'{height}mm')
    svg.set('width', f'{width}mm')
    svg.set('viewBox', viewBox)

    g = SubElement(svg, 'g', stroke="#000000", fill="#C4E9FB", stroke_linecap="round", stroke_width="0.15", transform=transform)
    p = SubElement(g, 'path', d=path)
    
    # Add offset path if provided
    if offset > 0 and offset_path:
        offset_g = SubElement(svg, 'g', stroke="#FF0000", fill="none", stroke_linecap="round", stroke_width="0.1", transform=transform)
        offset_p = SubElement(offset_g, 'path', d=offset_path)

    # Add dimension text if parameters are provided
    if label_height is not None and label_width is not None and top_diameter is not None and bottom_diameter is not None:
        # Calculate center position and appropriate font size
        center_x = width / 2
        center_y = height / 2
        
        # Calculate font size based on label dimensions (smaller labels = smaller text)
        base_font_size = min(width, height) / 15  # Adaptive font size
        font_size = max(3, min(base_font_size, 8))  # Keep between 3 and 8
        line_height = font_size * 1.3
        
        # Create text group with center alignment
        text_g = SubElement(svg, 'g')
        
        # Calculate starting Y position to center all text vertically
        total_lines = 3 if overlap else 2
        if top_diameter == bottom_diameter:
            total_lines = 2 if not overlap else 3
        
        text_y_start = center_y - (total_lines * line_height) / 2 + line_height
        
        # Label dimensions
        text1 = SubElement(text_g, 'text', x=str(center_x), y=str(text_y_start), 
                          fill="black", stroke="none", 
                          style=f"font-family:Arial,sans-serif;font-size:{font_size}px;font-weight:bold;text-anchor:middle")
        text1.text = f"Label: {label_height}×{label_width}mm"
        
        # Diameter information
        if top_diameter != bottom_diameter:
            text2 = SubElement(text_g, 'text', x=str(center_x), y=str(text_y_start + line_height), 
                              fill="black", stroke="none", 
                              style=f"font-family:Arial,sans-serif;font-size:{font_size}px;font-weight:bold;text-anchor:middle")
            text2.text = f"⌀ {top_diameter}mm - {bottom_diameter}mm"
        else:
            text2 = SubElement(text_g, 'text', x=str(center_x), y=str(text_y_start + line_height), 
                              fill="black", stroke="none", 
                              style=f"font-family:Arial,sans-serif;font-size:{font_size}px;font-weight:bold;text-anchor:middle")
            text2.text = f"⌀ {top_diameter}mm (cylindrical)"

        # Overlap details
        if overlap:
            text3 = SubElement(text_g, 'text', x=str(center_x), y=str(text_y_start + 2 * line_height),
                               fill="red", stroke="none",
                               style=f"font-family:Arial,sans-serif;font-size:{font_size}px;font-weight:bold;text-anchor:middle")
            text3.text = f"⚠ Overlap: {overlap_amount:.1f}mm"

    return svg

def save_svg(svg, filename):
    xml_string = minidom.parseString(tostring(svg)).toprettyxml(indent="    ")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_string)

def validate_input(label_height, label_width, top_diameter, bottom_diameter, offset):
    try:
        label_height = float(label_height)
        label_width = float(label_width)
        top_diameter = float(top_diameter)
        bottom_diameter = float(bottom_diameter)
        offset = float(offset)
    except ValueError:
        return False
    return True

def generate_conical_label(label_height, label_width, top_diameter, bottom_diameter, offset):
    if not validate_input(label_height, label_width, top_diameter, bottom_diameter, offset):
        blink_label()
        return "Error: Please enter numeric values."
        
    label_height = float(label_height)
    label_width = float(label_width)
    top_diameter = float(top_diameter)
    bottom_diameter = float(bottom_diameter)
    offset = float(offset)

    a = 0
    r = 0
    path = ""
    j = False
    overlap = False

    if top_diameter != bottom_diameter:
        j = top_diameter >= bottom_diameter
        u = max(top_diameter, bottom_diameter) / 2
        d = min(top_diameter, bottom_diameter) / 2
        p = u - d

        if p > label_height:
            blink_label()
            return "The difference between the two diameters is \n greater than the height of the label."            

        _ = min(max(p / label_height, -1), 1)
        e = u / _
        n = d / _
        t = 2 * label_width / (e + n)
        N = t * e
        A = t * n

        # Overlap detection and calculation
        overlap_amount = 0
        if N > math.pi * u * 2 or A > math.pi * d * 2:
            overlap = True
            # Calculate overlap amount (maximum of top or bottom overlap)
            top_circumference = math.pi * u * 2
            bottom_circumference = math.pi * d * 2
            top_overlap = max(0, N - top_circumference)
            bottom_overlap = max(0, A - bottom_circumference)
            overlap_amount = max(top_overlap, bottom_overlap)

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
        path = f"M {E} {k} L {D} {S}"
        path += f" A {e} {e}, 0, {g}, 0, {T} {z}"
        path += f" L {M} {F}"
        path += f" A {n} {n}, 0, {g}, 1, {E} {k}"
        path += " Z"
    else:
        # For cylindrical labels, check for overlap
        overlap_amount = 0
        circumference = math.pi * top_diameter
        if label_width > circumference:
            overlap = True
            overlap_amount = label_width - circumference
        
        a = label_width
        r = label_height
        path = f"M 0 0 V {label_height} H {label_width} V 0 Z"

    # Calculate offset path
     
    if offset > 0:
        if top_diameter != bottom_diameter:
            # For conical labels, create offset path
            offset_u = (max(top_diameter, bottom_diameter) + 2 * offset) / 2
            offset_d = (min(top_diameter, bottom_diameter) + 2 * offset) / 2
            offset_p = offset_u - offset_d
            epsilon = 1e-6
            if offset_p <= label_height:
                offset_ = min(max(offset_p / label_height, -1 + epsilon), 1 - epsilon)
                if abs(offset_) > epsilon:
                    offset_e = offset_u / offset_
                    offset_n = offset_d / offset_
                    offset_t = 2 * label_width / (offset_e + offset_n)
                    offset_v = offset_t > math.pi
                    offset_a = 2 * offset_e * (1 if offset_v else math.sin(offset_t / 2))
                    offset_P = offset_e * math.cos(offset_t / 2)
                    offset_L = offset_n * math.cos(offset_t / 2)
                    offset_r = offset_e - min(offset_P, offset_L)
                    offset_i = offset_a / 2
                    offset_c = offset_r - offset_e
                    offset_w = math.sin(-offset_t / 2)
                    offset_O = math.cos(-offset_t / 2)
                    offset_x = math.sin(offset_t / 2)
                    offset_C = math.cos(offset_t / 2)
                    offset_E = offset_i + offset_w * offset_n
                    offset_k = offset_c + offset_O * offset_n
                    offset_D = offset_i + offset_w * offset_e
                    offset_S = offset_c + offset_O * offset_e
                    offset_M = offset_i + offset_x * offset_n
                    offset_F = offset_c + offset_C * offset_n
                    offset_T = offset_i + offset_x * offset_e
                    offset_z = offset_c + offset_C * offset_e
                    offset_g = 1 if offset_v else 0
                    offset_path = f"M {offset_E} {offset_k} L {offset_D} {offset_S}"
                    offset_path += f" A {offset_e} {offset_e}, 0, {offset_g}, 0, {offset_T} {offset_z}"
                    offset_path += f" L {offset_M} {offset_F}"
                    offset_path += f" A {offset_n} {offset_n}, 0, {offset_g}, 1, {offset_E} {offset_k}"
                    offset_path += " Z"
        else:
            # For cylindrical labels, create rectangular offset
            offset_path = f"M {-offset} {-offset} V {label_height + offset} H {label_width + offset} V {-offset} Z"

    s = 0.5
    viewBox = f"{-s} {' '.join([str(s) if j else str(-s), str(a + s * 2), str(r + s * 2)])}"
    transform = f"translate(0, {r + s * 2}) scale(1,-1)" if j else ""

    svg = create_svg(a + s * 2, r + s * 2, viewBox, path, transform, label_height, label_width, top_diameter, bottom_diameter, overlap, overlap_amount, offset, offset_path)

    # Return svg, overlap status, and overlap amount
    return svg, overlap, overlap_amount

def show_preview():
    """Generate and display a preview of the label"""
    label_height = label_height_entry.get()
    label_width = label_width_entry.get()
    top_diameter = top_diameter_entry.get()
    bottom_diameter = bottom_diameter_entry.get()
    offset = offset_entry.get()

    result = generate_conical_label(label_height, label_width, top_diameter, bottom_diameter, offset)

    if isinstance(result, str):
        result_label.configure(text=result, fg="red")
        return

    svg, overlap, overlap_amount = result
    
    # Create temporary SVG file for preview
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, "preview_label.svg")
    save_svg(svg, temp_file)
    
    # Open preview in default browser
    webbrowser.open(f"file:///{temp_file}")
    
    # Update status message
    msg = f"Preview generated for {label_height}x{label_width}mm label"
    if overlap:
        msg += f"\nWarning: Label overlaps by {overlap_amount:.1f}mm"
        result_label.configure(text=msg, fg="orange")
    else:
        result_label.configure(text=msg, fg="blue")

def generate_label():
    """Generate and save the label"""
    label_height = label_height_entry.get()
    label_width = label_width_entry.get()
    top_diameter = top_diameter_entry.get()
    bottom_diameter = bottom_diameter_entry.get()
    offset = offset_entry.get()

    result = generate_conical_label(label_height, label_width, top_diameter, bottom_diameter, offset)

    if isinstance(result, str):
        result_label.configure(text=result, fg="red")
    else:
        svg, overlap, overlap_amount = result
        file_extension = ".svg"
        file_name = f"TaperLabel {label_height}x{label_width}{file_extension}"
        file_path = filedialog.asksaveasfilename(defaultextension=file_extension, initialfile=file_name, filetypes=[("SVG files", "*.svg")])
        if file_path:
            save_svg(svg, file_path)
            webbrowser.open(file_path)
            msg = f"Label {label_height}x{label_width}.svg\nwas saved successfully."
            if overlap:
                msg += f"\nWarning: The label overlaps by {overlap_amount:.1f}mm."
                result_label.configure(text=msg, fg="orange")
            else:
                result_label.configure(text=msg, fg="green")
def blink_label():
    current_color = result_label.cget("foreground")
    new_color = "red" if current_color == "black" else "black"
    result_label.configure(fg=new_color)
    result_label.after(1000, blink_label)  # Flashing color

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"+{x}+{y}")

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x = y = 0
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        tooltip_label = tk.Label(self.tooltip_window, text=self.text, background="#FFFFE0", relief="solid", borderwidth=1)
        tooltip_label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

window = tk.Tk()
window.title("Taper Label Generator | VIW ")
window.geometry("407x280")  # Increased height for offset field
window.resizable(False, False)  # Disable resizing and full screen

label_height_label = tk.Label(window, text="Label height (mm):")
label_height_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
label_height_entry = tk.Entry(window, width=35)
label_height_entry.grid(row=0, column=1, padx=10, pady=5)
label_height_entry.insert(0, "60")  # Default value
Tooltip(label_height_entry, "Enter the height of the label")

label_width_label = tk.Label(window, text="Label width (mm):")
label_width_label.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
label_width_entry = tk.Entry(window, width=35)
label_width_entry.grid(row=1, column=1, padx=10, pady=5)
label_width_entry.insert(0, "195")  # Default value
Tooltip(label_width_entry, "Enter the width of the label")

top_diameter_label = tk.Label(window, text="Upper diameter (mm):")
top_diameter_label.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
top_diameter_entry = tk.Entry(window, width=35)
top_diameter_entry.grid(row=2, column=1, padx=10, pady=5)
top_diameter_entry.insert(0, "47")  # Default value
Tooltip(top_diameter_entry, "Enter the top diameter of the cone")

bottom_diameter_label = tk.Label(window, text="Bottom diameter (mm):")
bottom_diameter_label.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
bottom_diameter_entry = tk.Entry(window, width=35)
bottom_diameter_entry.grid(row=3, column=1, padx=10, pady=5)
bottom_diameter_entry.insert(0, "70")  # Default value
Tooltip(bottom_diameter_entry, "Enter the bottom diameter of the cone")

offset_label = tk.Label(window, text="Offset (mm):")
offset_label.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
offset_entry = tk.Entry(window, width=35)
offset_entry.grid(row=4, column=1, padx=10, pady=5)
offset_entry.insert(0, "2")  # Default value
Tooltip(offset_entry, "Enter the offset distance around the label")

preview_button = tk.Button(window, width=20, height=2, text="Preview Label", command=show_preview, bg="lightblue")
preview_button.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
Tooltip(preview_button, "Generate and preview the label in your browser")

generate_button = tk.Button(window, width=20, height=2, text="Create a label", command=generate_label, bg="white")
generate_button.grid(row=6, column=0, padx=10, pady=5, sticky="nsew")

result_label = tk.Label(window, text="")
result_label.grid(row=5, column=1, padx=10, pady=5, columnspan=2, rowspan=2)

center_window(window)
window.mainloop()
