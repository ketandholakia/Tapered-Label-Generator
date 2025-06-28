import math
import tkinter as tk
import webbrowser
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from tkinter import filedialog

def create_svg(width, height, viewBox, path, transform):
    svg = Element('svg', {'version': "1.1", 'baseProfile': "tiny", 'xmlns': "http://www.w3.org/2000/svg", 'xmlns:xlink': "http://www.w3.org/1999/xlink"})
    svg.set('height', f'{height}mm')
    svg.set('width', f'{width}mm')
    svg.set('viewBox', viewBox)

    g = SubElement(svg, 'g', stroke="#000000", fill="#C4E9FB", stroke_linecap="round", stroke_width="0.15", transform=transform)
    p = SubElement(g, 'path', d=path)

    return svg

def save_svg(svg, filename):
    xml_string = minidom.parseString(tostring(svg)).toprettyxml(indent="    ")
    with open(filename, 'w') as f:
        f.write(xml_string)

def validate_input(label_height, label_width, top_diameter, bottom_diameter):
    try:
        label_height = float(label_height)
        label_width = float(label_width)
        top_diameter = float(top_diameter)
        bottom_diameter = float(bottom_diameter)
    except ValueError:
        return False
    return True

def generate_conical_label(label_height, label_width, top_diameter, bottom_diameter):
    if not validate_input(label_height, label_width, top_diameter, bottom_diameter):
        blink_label()  # Start the blinking effect
        return "Error: Please enter numeric values."
        
    label_height = float(label_height)
    label_width = float(label_width)
    top_diameter = float(top_diameter)
    bottom_diameter = float(bottom_diameter)

    a = 0
    r = 0
    path = ""
    j = False

    if top_diameter != bottom_diameter:
        j = top_diameter >= bottom_diameter
        u = max(top_diameter, bottom_diameter) / 2
        d = min(top_diameter, bottom_diameter) / 2
        p = u - d

        if p > label_height:
            blink_label()  # Start the blinking effect
            return "The difference between the two diameters is \n greater than the height of the label."            

        _ = min(max(p / label_height, -1), 1)
        e = u / _
        n = d / _
        t = 2 * label_width / (e + n)
        N = t * e
        A = t * n

        if N > math.pi * u * 2 or A > math.pi * d * 2:
            blink_label()  # Start the blinking effect
            return "The label will circle the surface more than once."

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
        path += " Z"  # Closing the loop
    else:
        a = label_width
        r = label_height
        path = f"M 0 0 V {label_height} H {label_width} V 0 Z"  # Closing the loop

    s = 0.5
    viewBox = f"{-s} {' '.join([str(s) if j else str(-s), str(a + s * 2), str(r + s * 2)])}"
    transform = f"translate(0, {r + s * 2}) scale(1,-1)" if j else ""

    return create_svg(a + s * 2, r + s * 2, viewBox, path, transform)

def generate_label():
    label_height = label_height_entry.get()
    label_width = label_width_entry.get()
    top_diameter = top_diameter_entry.get()
    bottom_diameter = bottom_diameter_entry.get()

    svg = generate_conical_label(label_height, label_width, top_diameter, bottom_diameter)

    if isinstance(svg, str):
        result_label.configure(text=svg)        
    else:
        file_extension = ".svg"
        file_name = f"TaperLabel {label_height}x{label_width}{file_extension}"
        file_path = filedialog.asksaveasfilename(defaultextension=file_extension, initialfile=file_name, filetypes=[("SVG files", "*.svg")])
        if file_path:
            save_svg(svg, file_path)
            webbrowser.open(file_path)
            result_label.configure(text=f"Label {label_height}x{label_width}.svg\nwas saved successfully.", fg="green")

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
window.title("Taper Label Generator 1.0.0 | YanaShine")
window.geometry("550x165")  # Fixed window width
window.resizable(False, False)  # Disable resizing and full screen

label_height_label = tk.Label(window, text="Label height (mm):")
label_height_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
label_height_entry = tk.Entry(window, width=35)
label_height_entry.grid(row=0, column=1, padx=10, pady=5)
Tooltip(label_height_entry, "Enter the height of the label")

label_width_label = tk.Label(window, text="Label width (mm):")
label_width_label.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
label_width_entry = tk.Entry(window, width=35)
label_width_entry.grid(row=1, column=1, padx=10, pady=5)
Tooltip(label_width_entry, "Enter the width of the label")

top_diameter_label = tk.Label(window, text="Upper diameter (mm):")
top_diameter_label.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
top_diameter_entry = tk.Entry(window, width=35)
top_diameter_entry.grid(row=2, column=1, padx=10, pady=5)
Tooltip(top_diameter_entry, "Enter the top diameter of the cone")

bottom_diameter_label = tk.Label(window, text="Bottom diameter (mm):")
bottom_diameter_label.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
bottom_diameter_entry = tk.Entry(window, width=35)
bottom_diameter_entry.grid(row=3, column=1, padx=10, pady=5)
Tooltip(bottom_diameter_entry, "Enter the bottom diameter of the cone")

generate_button = tk.Button(window, width=20, height=2, text="Create a label", command=generate_label, bg="white")
generate_button.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

result_label = tk.Label(window, text="")
result_label.grid(row=4, column=1, padx=10, pady=5, columnspan=2)

center_window(window)
window.mainloop()
