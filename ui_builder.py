import json
import os
import tkinter as tk
from tkinter import messagebox, filedialog, messagebox

PADDING = 100
current_tool = None
selected_item = None
drag_data = {"x": 0, "y": 0}
preview_item = None
is_dragging = False
ui_objects = []
selection_box = None

text_entry = None
font_size_entry = None
fill_entry = None
outline_entry = None
properties_panel = None
text_label = None
font_label = None
fill_label = None
outline_label = None
apply_btn = None
builder_canvas = None

# ---- Updated COLOR MAP ----
COLOR_MAP = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
    "skyblue": "#87CEEB",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    # add more as needed
}

current_project_name = None
current_project_path = None
canvas_width_global = 400
canvas_height_global = 300

def create_ui_dimensions_window():
    """
    Ask user for UI dimensions after project is chosen.
    """
    def submit_dimensions():
        try:
            width = int(width_entry.get())
            height = int(height_entry.get())
            if width <= 0 or height <= 0:
                raise ValueError
            dimension_window.destroy()
            create_canvas(width, height)
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter valid positive integers for width and height")

    dimension_window = tk.Toplevel(root)
    dimension_window.title("UI Dimensions")
    dimension_window.geometry("300x150")

    tk.Label(dimension_window, text="Enter UI Width:").pack(pady=5)
    width_entry = tk.Entry(dimension_window)
    width_entry.pack()

    tk.Label(dimension_window, text="Enter UI Height:").pack(pady=5)
    height_entry = tk.Entry(dimension_window)
    height_entry.pack()

    tk.Button(dimension_window, text="Submit", command=submit_dimensions).pack(pady=10)

def color_to_rgb565(color_str):
    """
    Convert a color name or hex string to RGB565.
    Accepts:
        - Named colors from COLOR_MAP
        - "#RRGGBB" or "0xRRGGBB"
    Returns:
        - Hex string in 0xFFFF format
    """
    if not color_str:
        return "0xFFFF"  # default to white

    color_str = color_str.strip().lower()

    # Check if it's a named color
    if color_str in COLOR_MAP:
        color_str = COLOR_MAP[color_str]

    # Remove # or 0x if present
    if color_str.startswith("#"):
        color_str = color_str[1:]
    elif color_str.startswith("0x"):
        color_str = color_str[2:]

    # Must have exactly 6 hex digits
    if len(color_str) != 6:
        return "0xFFFF"

    try:
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
    except ValueError:
        return "0xFFFF"

    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return f"0x{rgb565:04X}"

def set_tool(tool):
    global current_tool
    current_tool = tool

def create_canvas(ui_width, ui_height):
    global properties_panel
    global text_entry, font_size_entry
    global fill_entry, outline_entry
    global text_label, font_label
    global fill_label, outline_label
    global apply_btn
    global builder_canvas
        
    global canvas_width_global, canvas_height_global
    canvas_width_global = ui_width
    canvas_height_global = ui_height

    try:
        # ui_width = int(width_entry.get())
        # ui_height = int(height_entry.get())

        canvas_width = ui_width + (PADDING * 2)
        canvas_height = ui_height + (PADDING * 2)

        # New window
        builder = tk.Toplevel(root)
        def close_builder():
            builder.destroy()
            root.destroy()   # This fully exits app

        builder.protocol("WM_DELETE_WINDOW", close_builder)
        builder.title("Simple UI Builder")

        # ---- Left Toolbox ----
        toolbox = tk.Frame(builder, width=150, bg="#dddddd")
        toolbox.pack(side="left", fill="y")

        tk.Label(toolbox, text="Tools", bg="#dddddd",
                 font=("Arial", 12, "bold")).pack(pady=10)

        tk.Button(toolbox, text="Text", width=15,
                  command=lambda: set_tool("text")).pack(pady=5)

        tk.Button(toolbox, text="Rectangle", width=15,
                  command=lambda: set_tool("rectangle")).pack(pady=5)

        tk.Button(toolbox, text="Oval", width=15,
                  command=lambda: set_tool("oval")).pack(pady=5)
        
        # ---- Properties Panel ----
        properties_panel = tk.Frame(builder, width=200, bg="#f0f0f0")
        properties_panel.pack(side="right", fill="y")

        tk.Label(properties_panel, text="Properties",
                bg="#f0f0f0",
                font=("Arial", 12, "bold")).pack(pady=10)

        # Text content
        text_label = tk.Label(properties_panel, text="Text:", bg="#f0f0f0")
        text_label.pack()
        text_entry = tk.Entry(properties_panel)
        text_entry.pack(pady=5)

        # Font size
        font_label = tk.Label(properties_panel, text="Font Size:", bg="#f0f0f0")
        font_label.pack()
        font_size_entry = tk.Entry(properties_panel)
        font_size_entry.pack(pady=5)

        # Fill color
        fill_label = tk.Label(properties_panel, text="Fill Color:", bg="#f0f0f0")
        fill_label.pack()
        fill_entry = tk.Entry(properties_panel)
        fill_entry.pack(pady=5)

        # Outline color
        outline_label = tk.Label(properties_panel, text="Outline Color:", bg="#f0f0f0")
        outline_label.pack()
        outline_entry = tk.Entry(properties_panel)
        outline_entry.pack(pady=5)

        # Apply button
        apply_btn = tk.Button(
            properties_panel,
            text="Apply Changes",
            command=lambda: apply_properties(
                canvas,
                text_entry,
                font_size_entry,
                fill_entry,
                outline_entry
            )
        )
        apply_btn.pack(pady=10)

        # =========================
        # Right Container (Canvas + Button)
        # =========================
        right_container = tk.Frame(builder)
        right_container.pack(side="right", fill="both", expand=True)

        # ---- Canvas Area ----
        canvas = tk.Canvas(
            right_container,
            width=canvas_width,
            height=canvas_height,
            bg="lightgray"
        )
        canvas.pack()

        # UI layout boundary (white area)
        canvas.create_rectangle(
            PADDING,
            PADDING,
            PADDING + ui_width,
            PADDING + ui_height,
            fill="white",
            outline="black",
            width=2,
            tags="ui_area"
        )
        
        builder_canvas = canvas

        # =========================
        # Bottom Frame (Inside Builder Window)
        # =========================
        bottom_frame = tk.Frame(right_container)
        bottom_frame.pack(fill="x", pady=10)

        save_btn = tk.Button(
            bottom_frame,
            text="Save Project",
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            command=save_project
        )
        save_btn.pack(side="left", padx=10)

        generate_btn = tk.Button(
            bottom_frame,
            text="Generate C Code",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            command=generate_c_code
        )
        generate_btn.pack(side="right", padx=10)

        # =========================
        # Mouse Bindings
        # =========================
        canvas.bind("<Motion>", lambda e: show_preview(e, canvas))
        canvas.bind("<Button-1>", lambda e: handle_click(e, canvas))
        canvas.bind("<B1-Motion>", lambda e: drag_item(e, canvas))
        canvas.bind("<ButtonRelease-1>", stop_drag)

        # =========================
        # Right-click Context Menu
        # =========================
        context_menu = tk.Menu(builder, tearoff=0)
        context_menu.add_command(
            label="Bring to Front",
            command=lambda: bring_to_front(canvas)
        )
        context_menu.add_command(
            label="Send to Back",
            command=lambda: send_to_back(canvas)
        )

        canvas.bind("<Button-3>",
                    lambda e: show_context_menu(e, canvas, context_menu))

    except ValueError:
        messagebox.showerror("Invalid Input", "Enter valid numbers")
    
    return canvas

def apply_properties(canvas, text_entry, font_size_entry, fill_entry, outline_entry):
    global selected_item

    if not selected_item:
        return

    for obj in ui_objects:
        if obj["id"] == selected_item:

            # ----- TEXT UPDATE -----
            new_text = text_entry.get()
            if new_text:
                canvas.itemconfig(selected_item, text=new_text)
                obj["text"] = new_text

            # ----- FONT SIZE -----
            new_font_size = font_size_entry.get()
            if new_font_size:
                canvas.itemconfig(selected_item,
                                  font=("Arial", int(new_font_size)))
                obj["font_size"] = int(new_font_size)

            # ----- FILL COLOR -----
            # new_fill = fill_entry.get()
            # if new_fill:
            #     canvas.itemconfig(selected_item, fill=new_fill)
            #     obj["fill"] = new_fill
            new_fill = fill_entry.get().strip()
            if new_fill:
                if new_fill.lower() in COLOR_MAP:
                    new_fill = COLOR_MAP[new_fill.lower()]

                if not new_fill.startswith("#"):
                    if new_fill.startswith("0x"):
                        new_fill = "#" + new_fill[2:]
                    else:
                        new_fill = "#" + new_fill

                canvas.itemconfig(selected_item, fill=new_fill)
                obj["fill"] = new_fill

            # ----- OUTLINE COLOR -----
            # new_outline = outline_entry.get()
            # if new_outline:
            #     canvas.itemconfig(selected_item, outline=new_outline)
            #     obj["outline"] = new_outline

            # ----- OUTLINE COLOR -----
            new_outline = outline_entry.get().strip()
            if new_outline:
                if new_outline.lower() in COLOR_MAP:
                    new_outline = COLOR_MAP[new_outline.lower()]

                if not new_outline.startswith("#"):
                    if new_outline.startswith("0x"):
                        new_outline = "#" + new_outline[2:]
                    else:
                        new_outline = "#" + new_outline

                canvas.itemconfig(selected_item, outline=new_outline)
                obj["outline"] = new_outline

            break

def place_item(event, canvas):
    global selected_item, current_tool

    # Do nothing if no tool selected
    if current_tool is None:
        return

    # Allow placing only inside UI area
    if not (PADDING < event.x < canvas.winfo_width() - PADDING and
            PADDING < event.y < canvas.winfo_height() - PADDING):
        return

    if current_tool == "text":
        selected_item = canvas.create_text(
            event.x, event.y,
            text="Sample Text",
            font=("Arial", 12),
            tags="draggable"
        )

    elif current_tool == "rectangle":
        selected_item = canvas.create_rectangle(
            event.x, event.y,
            event.x + 100, event.y + 50,
            fill="skyblue",
            tags="draggable"
        )

    elif current_tool == "oval":
        selected_item = canvas.create_oval(
            event.x, event.y,
            event.x + 100, event.y + 60,
            fill="lightgreen",
            tags="draggable"
        )

    # Save drag start position
    if selected_item:
        drag_data["x"] = event.x
        drag_data["y"] = event.y

        # 🔥 RESET TOOL AFTER ONE USE
        current_tool = None

def generate_c_code():
    c_code = ""

    # ----- Headers -----
    c_code += "#include <stdint.h>\n\n"

    # ----- Enum -----
    c_code += "typedef enum {\n"
    c_code += "    UI_RECTANGLE,\n"
    c_code += "    UI_OVAL,\n"
    c_code += "    UI_TEXT\n"
    c_code += "} UI_ObjectType;\n\n"

    # ----- Struct -----
    c_code += "typedef struct {\n"
    c_code += "    UI_ObjectType type;\n"
    c_code += "    int x;\n"
    c_code += "    int y;\n"
    c_code += "    int width;\n"
    c_code += "    int height;\n"
    c_code += "    uint16_t fill;        // RGB565 fill color\n"
    c_code += "    uint16_t outline;     // RGB565 outline color\n"
    c_code += "    int font_size;        // used only for TEXT\n"
    c_code += "    char text[50];\n"
    c_code += "} UI_Object;\n\n"

    # ----- UI Object Count -----
    c_code += f"#define UI_OBJECT_COUNT {len(ui_objects)}\n\n"

    # ----- UI Objects Array -----
    c_code += "UI_Object ui_objects[UI_OBJECT_COUNT] = {\n"

    for obj in ui_objects:
        # Convert fill and outline to RGB565
        fill = color_to_rgb565(obj.get("fill", "white"))
        outline = color_to_rgb565(obj.get("outline", "black"))
        font_size = obj.get("font_size", 12)
        text_val = obj.get("text", "")

        if obj["type"] == "RECTANGLE":
            c_code += (
                f"    {{UI_RECTANGLE, {obj['x']}, {obj['y']}, "
                f"{obj['width']}, {obj['height']}, {fill}, {outline}, 0, \"\"}},  // Rectangle\n"
            )

        elif obj["type"] == "OVAL":
            c_code += (
                f"    {{UI_OVAL, {obj['x']}, {obj['y']}, "
                f"{obj['width']}, {obj['height']}, {fill}, {outline}, 0, \"\"}},  // Oval\n"
            )

        elif obj["type"] == "TEXT":
            c_code += (
                f"    {{UI_TEXT, {obj['x']}, {obj['y']}, "
                f"0, 0, {fill}, 0x0000, {font_size}, \"{text_val}\"}},  // Text\n"
            )

    c_code += "};\n"

    # ----- Show in Popup -----
    code_window = tk.Toplevel()
    code_window.title("Generated C Code")

    text_area = tk.Text(code_window, width=80, height=30)
    text_area.pack()
    text_area.insert("1.0", c_code)

def show_preview(event, canvas):
    global preview_item

    if current_tool is None:
        if preview_item:
            canvas.delete(preview_item)
            preview_item = None
        return

    # Only preview inside UI area
    if not (PADDING < event.x < canvas.winfo_width() - PADDING and
            PADDING < event.y < canvas.winfo_height() - PADDING):
        if preview_item:
            canvas.delete(preview_item)
            preview_item = None
        return

    # Delete old preview
    if preview_item:
        canvas.delete(preview_item)

    if current_tool == "rectangle":
        preview_item = canvas.create_rectangle(
            event.x, event.y,
            event.x + 100, event.y + 50,
            outline="blue",
            dash=(4, 2)
        )

    elif current_tool == "oval":
        preview_item = canvas.create_oval(
            event.x, event.y,
            event.x + 100, event.y + 60,
            outline="green",
            dash=(4, 2)
        )

    elif current_tool == "text":
        preview_item = canvas.create_text(
            event.x, event.y,
            text="Sample Text",
            fill="gray"
        )

def handle_click(event, canvas):
    global selected_item, current_tool, preview_item, is_dragging

    # -------- PLACE MODE --------
    if current_tool:

        if not (PADDING < event.x < canvas.winfo_width() - PADDING and
                PADDING < event.y < canvas.winfo_height() - PADDING):
            return

        # RECTANGLE
        if current_tool == "rectangle":
            selected_item = canvas.create_rectangle(
                event.x, event.y,
                event.x + 100, event.y + 50,
                fill="skyblue",
                tags=("draggable", "objects")
            )

            ui_objects.append({
                "id": selected_item,
                "type": "RECTANGLE",
                "x": event.x,
                "y": event.y,
                "width": 100,
                "height": 50,
                "text": "",
                "font_size": 0,
                "fill": "skyblue",
                "outline": "black"
            })

        # OVAL
        elif current_tool == "oval":
            selected_item = canvas.create_oval(
                event.x, event.y,
                event.x + 100, event.y + 60,
                fill="lightgreen",
                tags=("draggable", "objects")
            )

            ui_objects.append({
                "id": selected_item,
                "type": "OVAL",
                "x": event.x,
                "y": event.y,
                "width": 100,
                "height": 60,
                "text": "",
                "font_size": 0,
                "fill": "lightgreen",
                "outline": "black"
            })

        # TEXT
        elif current_tool == "text":
            selected_item = canvas.create_text(
                event.x, event.y,
                text="Sample Text",
                font=("Arial", 12),
                tags=("draggable", "objects")
            )

            ui_objects.append({
                "id": selected_item,
                "type": "TEXT",
                "x": event.x,
                "y": event.y,
                "width": 0,
                "height": 0,
                "text": "Sample Text",
                "font_size": 12,
                "fill": "black",
                "outline": ""
            })

        # Remove preview
        if preview_item:
            canvas.delete(preview_item)
            preview_item = None

        current_tool = None
        selected_item = None
        return

    # -------- SELECT MODE --------
    clicked = canvas.find_closest(event.x, event.y)

    if clicked and "draggable" in canvas.gettags(clicked[0]):
        selected_item = clicked[0]
        item_type = canvas.type(selected_item)

        # ---- Highlight selected object ----
        highlight_selected(canvas, selected_item)

        # ---- Show only relevant properties ----
        update_properties_visibility(item_type)

        # ---- POPULATE PROPERTY FIELDS ----
        if item_type == "text":
            text_entry.delete(0, tk.END)
            text_entry.insert(0, canvas.itemcget(selected_item, "text"))
            font_size_entry.delete(0, tk.END)
            font_size_entry.insert(0, canvas.itemcget(selected_item, "font").split()[1])
            fill_entry.delete(0, tk.END)
            fill_entry.insert(0, canvas.itemcget(selected_item, "fill"))

        elif item_type in ["rectangle", "oval"]:
            fill_entry.delete(0, tk.END)
            fill_entry.insert(0, canvas.itemcget(selected_item, "fill"))
            outline_entry.delete(0, tk.END)
            outline_entry.insert(0, canvas.itemcget(selected_item, "outline"))

        drag_data["x"] = event.x
        drag_data["y"] = event.y
        is_dragging = True
    else:
        selected_item = None
        highlight_selected(canvas, None)
        update_properties_visibility(None)

def drag_item(event, canvas):
    global selected_item, is_dragging

    if selected_item and is_dragging:
        dx = event.x - drag_data["x"]
        dy = event.y - drag_data["y"]

        canvas.move(selected_item, dx, dy)
        highlight_selected(canvas, selected_item)

        drag_data["x"] = event.x
        drag_data["y"] = event.y

        for obj in ui_objects:
            if obj["id"] == selected_item:
                obj["x"] += dx
                obj["y"] += dy

def stop_drag(event):
    global is_dragging
    is_dragging = False

def show_context_menu(event, canvas, menu):
    global selected_item

    clicked = canvas.find_closest(event.x, event.y)

    if clicked and "draggable" in canvas.gettags(clicked[0]):
        selected_item = clicked[0]
        menu.post(event.x_root, event.y_root)

def bring_to_front(canvas):
    global selected_item

    if selected_item:
        canvas.tag_raise(selected_item)

def send_to_back(canvas):
    global selected_item

    if selected_item:
        # Lower only within draggable group,
        # but keep above UI background
        canvas.tag_lower(selected_item)
        canvas.tag_raise(selected_item, "ui_area")

def highlight_selected(canvas, item_id):
    global selection_box

    # Remove old selection box
    if selection_box:
        canvas.delete(selection_box)
        selection_box = None

    if not item_id:
        return

    # Get bounding box of item
    bbox = canvas.bbox(item_id)
    if not bbox:
        return

    x1, y1, x2, y2 = bbox

    # Create dashed blue border
    selection_box = canvas.create_rectangle(
        x1 - 4, y1 - 4,
        x2 + 4, y2 + 4,
        outline="blue",
        dash=(4, 2),
        width=2
    )

    # Keep selection border always on top
    canvas.tag_raise(selection_box)

def update_properties_visibility(item_type):
    """
    Show only the applicable property widgets based on the selected item type.
    Hide all others.
    """
    # First hide everything
    text_label.pack_forget()
    text_entry.pack_forget()
    font_label.pack_forget()
    font_size_entry.pack_forget()
    fill_label.pack_forget()
    fill_entry.pack_forget()
    outline_label.pack_forget()
    outline_entry.pack_forget()
    apply_btn.pack_forget()

    if item_type == "text":
        text_label.pack()
        text_entry.pack(pady=5)
        font_label.pack()
        font_size_entry.pack(pady=5)
        fill_label.pack()
        fill_entry.pack(pady=5)
        # Don't show outline for text!
        # outline_label.pack_forget()
        # outline_entry.pack_forget()
        apply_btn.pack(pady=10)

    elif item_type in ["rectangle", "oval"]:
        # Shape-specific properties
        fill_label.pack()
        fill_entry.pack(pady=5)
        outline_label.pack()
        outline_entry.pack(pady=5)
        apply_btn.pack(pady=10)

    else:
        text_label.pack_forget()
        text_entry.pack_forget()
        font_label.pack_forget()
        font_size_entry.pack_forget()
        fill_label.pack_forget()
        fill_entry.pack_forget()
        outline_label.pack_forget()
        outline_entry.pack_forget()
        apply_btn.pack_forget()

def rgb888_to_rgb565(hex_color):
    """Convert #RRGGBB or 0xRRGGBB to RGB565 hex code safely"""
    if not hex_color:
        return "0xFFFF"  # default to white

    if isinstance(hex_color, str):
        hex_color = hex_color.strip()
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]
        elif hex_color.startswith("0x"):
            hex_color = hex_color[2:]

    # Ensure we have exactly 6 hex digits
    if len(hex_color) != 6:
        return "0xFFFF"  # fallback to white

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        return "0xFFFF"  # fallback to white if invalid

    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return f"0x{rgb565:04X}"


# def save_project():
#     if not current_project_path or not current_project_name:
#         messagebox.showerror("Error", "No project open!")
#         return

#     project_data = {
#         "project_name": current_project_name,
#         "ui_width": canvas.winfo_width() - 2 * PADDING,
#         "ui_height": canvas.winfo_height() - 2 * PADDING,
#         "ui_objects": ui_objects
#     }

#     file_path = os.path.join(current_project_path, "project.json")
#     with open(file_path, "w") as f:
#         json.dump(project_data, f, indent=4)

#     messagebox.showinfo("Saved", f"Project saved at {file_path}")

def open_existing_project():
    global current_project_name, current_project_path, ui_objects

    file_path = filedialog.askopenfilename(
        title="Open Project",
        filetypes=[("UI Project Files", "*.json")]
    )

    if not file_path:
        return

    try:
        with open(file_path, "r") as f:
            project_data = json.load(f)

        # Restore metadata
        current_project_name = project_data.get("project_name")
        current_project_path = os.path.dirname(file_path)
        ui_objects = project_data.get("ui_objects", [])

        ui_width = project_data.get("ui_width", 400)
        ui_height = project_data.get("ui_height", 300)

        # Hide start screen
        root.withdraw()

        # ✅ PASS WIDTH & HEIGHT HERE
        loaded_canvas = create_canvas(ui_width, ui_height)

        # Recreate objects
        for obj in ui_objects:
            obj_type = obj["type"]

            if obj_type == "RECTANGLE":
                obj["id"] = loaded_canvas.create_rectangle(
                    obj["x"], obj["y"],
                    obj["x"] + obj["width"],
                    obj["y"] + obj["height"],
                    fill=obj.get("fill", "skyblue"),
                    outline=obj.get("outline", "black"),
                    tags=("draggable", "objects")
                )

            elif obj_type == "OVAL":
                obj["id"] = loaded_canvas.create_oval(
                    obj["x"], obj["y"],
                    obj["x"] + obj["width"],
                    obj["y"] + obj["height"],
                    fill=obj.get("fill", "lightgreen"),
                    outline=obj.get("outline", "black"),
                    tags=("draggable", "objects")
                )

            elif obj_type == "TEXT":
                obj["id"] = loaded_canvas.create_text(
                    obj["x"], obj["y"],
                    text=obj.get("text", "Sample Text"),
                    font=("Arial", obj.get("font_size", 12)),
                    fill=obj.get("fill", "black"),
                    tags=("draggable", "objects")
                )

    except Exception as e:
        messagebox.showerror("Error", f"Failed to open project:\n{e}")
        
def load_objects_to_canvas():
    global builder_canvas, ui_objects

    for obj in ui_objects:
        obj_type = obj["type"]
        x = obj["x"]
        y = obj["y"]

        if obj_type == "text":
            builder_canvas.create_text(
                x, y,
                text=obj["text"],
                fill=obj["color"],
                font=("Arial", obj["size"])
            )

        elif obj_type == "rectangle":
            builder_canvas.create_rectangle(
                x, y,
                x + obj["width"],
                y + obj["height"],
                fill=obj["color"]
            )

def save_project():
    global ui_objects, current_project_name, current_project_path, builder_canvas

    if not ui_objects:
        messagebox.showwarning("Nothing to Save", "There are no UI elements to save!")
        return

    if not builder_canvas:
        messagebox.showerror("Error", "No active canvas found!")
        return

    save_path = filedialog.asksaveasfilename(
        title="Save Project",
        initialfile=f"{current_project_name}.json" if current_project_name else "project.json",
        defaultextension=".json",
        filetypes=[("UI Project JSON", "*.json")]
    )

    if not save_path:
        return

    project_data = {
        "project_name": current_project_name or "Unnamed",
        "ui_width": canvas_width_global,
        "ui_height": canvas_height_global,
        "ui_objects": []
    }

    # 🔥 Save in REAL canvas stacking order
    canvas_items = builder_canvas.find_all()

    for canvas_id in canvas_items:
        tags = builder_canvas.gettags(canvas_id)

        # Only save real UI objects
        if "objects" not in tags:
            continue

        for obj in ui_objects:
            if obj.get("id") == canvas_id:
                obj_copy = obj.copy()
                obj_copy.pop("id", None)
                project_data["ui_objects"].append(obj_copy)

    try:
        with open(save_path, "w") as f:
            json.dump(project_data, f, indent=4)

        messagebox.showinfo("Saved", f"Project saved successfully at:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save project:\n{e}")

    name = project_name_entry.get().strip()
    path = project_path_entry.get().strip()

    if not name:
        messagebox.showerror("Error", "Please enter project name")
        return

    if not path:
        messagebox.showerror("Error", "Please select project path")
        return

    current_project_name = name
    current_project_path = path

    # Hide project section
    project_frame.pack_forget()

    # Show dimension section
    dimension_frame.pack(pady=10, fill="x", padx=50)

# ================================
# Main Start Window
# ================================
# root = tk.Tk()
# root.title("Start New UI Project")
# root.geometry("500x400")

# tk.Label(root, text="Start a new UI Project").pack(pady=10)
# tk.Button(root, text="Create New Project", command=launch_builder_flow).pack(pady=5)
# tk.Button(root, text="Open Existing Project", command=open_existing_project).pack(pady=5)

# root.mainloop()

# ======================
# Logic Functions
# ======================

def show_create_section():
    dimension_frame.pack_forget()
    project_frame.pack(pady=10, fill="x", padx=50)


def validate_project_details():
    global current_project_name, current_project_path

    name = project_name_entry.get().strip()
    path = project_path_entry.get().strip()

    if not name:
        messagebox.showerror("Error", "Please enter project name")
        return

    if not path:
        messagebox.showerror("Error", "Please select project path")
        return

    current_project_name = name
    current_project_path = path

    project_frame.pack_forget()
    dimension_frame.pack(pady=10, fill="x", padx=50)


def create_project_from_ui():
    try:
        width = int(width_entry.get())
        height = int(height_entry.get())

        if width <= 0 or height <= 0:
            raise ValueError

        root.withdraw()  # Hide start screen
        create_canvas(width, height)

    except ValueError:
        messagebox.showerror("Error", "Enter valid width and height")


# ================================
# Main Start Window (Enhanced UX)
# ================================
root = tk.Tk()
root.title("Start New UI Project")
root.geometry("600x450")

# ----- Title -----
tk.Label(root, text="Start a new UI Project",
         font=("Arial", 14, "bold")).pack(pady=10)

# ----- Top Buttons -----
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

tk.Button(top_frame, text="Create New Project",
          command=lambda: show_create_section()).pack(side="left", padx=10)

tk.Button(top_frame, text="Open Existing Project",
          command=open_existing_project).pack(side="left", padx=10)


# ======================
# 🔴 PROJECT SECTION
# ======================
# ======================
# 🔴 PROJECT SECTION
# ======================
project_frame = tk.Frame(root, bd=2, relief="groove", padx=15, pady=15)
project_frame.pack(pady=10, fill="x", padx=50)

# Configure grid columns
project_frame.columnconfigure(0, weight=0)   # labels
project_frame.columnconfigure(1, weight=1)   # entry expands
project_frame.columnconfigure(2, weight=0)   # buttons

# ---- Project Name ----
tk.Label(project_frame, text="Project Name:").grid(row=0, column=0, sticky="w", pady=5)

project_name_entry = tk.Entry(project_frame)
project_name_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5)


# ---- Project Path ----
tk.Label(project_frame, text="Project Path:").grid(row=1, column=0, sticky="w", pady=5)

project_path_entry = tk.Entry(project_frame)
project_path_entry.grid(row=1, column=1, sticky="ew", pady=5)


def browse_path():
    path = filedialog.askdirectory()
    if path:
        project_path_entry.delete(0, tk.END)
        project_path_entry.insert(0, path)

# 🔴 Browse button (Right side)
tk.Button(project_frame, text="Browse", command=browse_path)\
    .grid(row=1, column=2, padx=10, pady=5)


# 🔵 Next button (Bottom Right)
tk.Button(project_frame, text="Next →",
          command=validate_project_details)\
    .grid(row=3, column=2, sticky="e", pady=15)


# ======================
# 🔵 DIMENSION SECTION
# ======================
dimension_frame = tk.Frame(root, bd=2, relief="groove", padx=10, pady=10)

tk.Label(dimension_frame, text="UI Width:").pack(anchor="w")
width_entry = tk.Entry(dimension_frame)
width_entry.pack(pady=5)

tk.Label(dimension_frame, text="UI Height:").pack(anchor="w")
height_entry = tk.Entry(dimension_frame)
height_entry.pack(pady=5)

tk.Button(dimension_frame, text="Create Project",
          command=lambda: create_project_from_ui()).pack(pady=10)


# Hide both initially
project_frame.pack_forget()
dimension_frame.pack_forget()

root.mainloop()