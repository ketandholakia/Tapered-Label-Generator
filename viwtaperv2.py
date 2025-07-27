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
    overlap = False  # Add overlap flag

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

        # Overlap detection
        if N > math.pi * u * 2 or A > math.pi * d * 2:
            overlap = True

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

    return create_svg(a + s * 2, r + s * 2, viewBox, path, transform, label_height, label_width, top_diameter, bottom_diameter), overlap

def generate_label():
    label_height = label_height_entry.get()
    label_width = label_width_entry.get()
    top_diameter = top_diameter_entry.get()
    bottom_diameter = bottom_diameter_entry.get()

    result = generate_conical_label(label_height, label_width, top_diameter, bottom_diameter)

    if isinstance(result, str):
        result_label.configure(text=result)        
    else:
        svg, overlap = result
        file_extension = ".svg"
        file_name = f"TaperLabel {label_height}x{label_width}{file_extension}"
        file_path = filedialog.asksaveasfilename(defaultextension=file_extension, initialfile=file_name, filetypes=[("SVG files", "*.svg")])
        if file_path:
            save_svg(svg, file_path)
            webbrowser.open(file_path)
            msg = f"Label {label_height}x{label_width}.svg\nwas saved successfully."
            if overlap:
                msg += "\nWarning: The label will overlap (wrap more than once around the surface)."
                result_label.configure(text=msg, fg="orange")
            else:
                result_label.configure(text=msg, fg="green")