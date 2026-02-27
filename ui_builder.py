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
canvas_width_global = 480
canvas_height_global = 272

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
    width_entry.insert(0, "480")
    width_entry.pack()

    tk.Label(dimension_window, text="Enter UI Height:").pack(pady=5)
    height_entry = tk.Entry(dimension_window)
    height_entry.insert(0, "272")
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

            # ----- FILL COLOR ----
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

# # def generate_c_code():
#     global current_project_path, current_project_name

#     if not current_project_path:
#         messagebox.showerror("Error", "No project path found!")
#         return

#     if not ui_objects:
#         messagebox.showwarning("Warning", "No UI objects to generate!")
#         return

#     # ===============================
#     # Build C Code String
#     # ===============================
#     c_code = ""

#     c_code += "#include <stdint.h>\n\n"

#     c_code += "typedef enum {\n"
#     c_code += "    UI_RECTANGLE,\n"
#     c_code += "    UI_OVAL,\n"
#     c_code += "    UI_TEXT\n"
#     c_code += "} UI_ObjectType;\n\n"

#     c_code += "typedef struct {\n"
#     c_code += "    UI_ObjectType type;\n"
#     c_code += "    int x;\n"
#     c_code += "    int y;\n"
#     c_code += "    int width;\n"
#     c_code += "    int height;\n"
#     c_code += "    uint16_t fill;\n"
#     c_code += "    uint16_t outline;\n"
#     c_code += "    int font_size;\n"
#     c_code += "    char text[50];\n"
#     c_code += "} UI_Object;\n\n"

#     c_code += f"#define UI_OBJECT_COUNT {len(ui_objects)}\n\n"
#     c_code += "UI_Object ui_objects[UI_OBJECT_COUNT] = {\n"

#     for obj in ui_objects:

#         fill = color_to_rgb565(obj.get("fill", "white"))
#         outline = color_to_rgb565(obj.get("outline", "black"))
#         font_size = obj.get("font_size", 12)
#         text_val = obj.get("text", "")

#         if obj["type"] == "RECTANGLE":
#             c_code += (
#                 f"    {{UI_RECTANGLE, {obj['x']}, {obj['y']}, "
#                 f"{obj['width']}, {obj['height']}, {fill}, {outline}, 0, \"\"}},\n"
#             )

#         elif obj["type"] == "OVAL":
#             c_code += (
#                 f"    {{UI_OVAL, {obj['x']}, {obj['y']}, "
#                 f"{obj['width']}, {obj['height']}, {fill}, {outline}, 0, \"\"}},\n"
#             )

#         elif obj["type"] == "TEXT":
#             c_code += (
#                 f"    {{UI_TEXT, {obj['x']}, {obj['y']}, "
#                 f"0, 0, {fill}, 0x0000, {font_size}, \"{text_val}\"}},\n"
#             )

#     c_code += "};\n"

#     # ===============================
#     # Create Folder Structure
#     # ===============================
#     src_path = os.path.join(current_project_path, "Core", "Src")
#     inc_path = os.path.join(current_project_path, "Core", "Inc")

#     os.makedirs(src_path, exist_ok=True)
#     os.makedirs(inc_path, exist_ok=True)

#     # ===============================
#     # Save File
#     # ===============================
#     file_path = os.path.join(src_path, "ui_layout.c")

#     try:
#         with open(file_path, "w") as f:
#             f.write(c_code)

#         messagebox.showinfo(
#             "Success",
#             f"C code generated successfully!\n\nSaved at:\n{file_path}"
#         )

#     except Exception as e:
#         messagebox.showerror("Error", f"Failed to write file:\n{e}")
#         return

#     # ===============================
#     # Optional: Show Preview Window
#     # ===============================
#     code_window = tk.Toplevel()
#     code_window.title("Generated C Code")

#     text_area = tk.Text(code_window, width=90, height=30)
#     text_area.pack()
#     text_area.insert("1.0", c_code)

def generate_c_code():
    """
    Generate C code for STM32H7 UI rendering with LTDC and DMA2D support.
    Creates files compatible with the STM32 CubeMX project structure.
    """
    global current_project_path

    if not current_project_path:
        messagebox.showerror("Error", "No project path found!")
        return

    if not ui_objects:
        messagebox.showwarning("Warning", "No UI objects to generate!")
        return

    inc_path = os.path.join(current_project_path, "Display", "Inc")
    src_path = os.path.join(current_project_path, "Display", "Src")

    os.makedirs(inc_path, exist_ok=True)
    os.makedirs(src_path, exist_ok=True)

    # ============================================
    # Build UI Object Entries
    # ============================================
    object_entries = ""

    for obj in ui_objects:
        fill = color_to_rgb565(obj.get("fill", "white"))
        outline = color_to_rgb565(obj.get("outline", "black"))
        font_size = obj.get("font_size", 12)
        text_val = obj.get("text", "")

        if obj["type"] == "RECTANGLE":
            object_entries += (
                f"    {{UI_RECTANGLE, {obj['x']}, {obj['y']}, "
                f"{obj['width']}, {obj['height']}, {fill}, {outline}, 0, \"\"}},\n"
            )

        elif obj["type"] == "OVAL":
            object_entries += (
                f"    {{UI_OVAL, {obj['x']}, {obj['y']}, "
                f"{obj['width']}, {obj['height']}, {fill}, {outline}, 0, \"\"}},\n"
            )

        elif obj["type"] == "TEXT":
            object_entries += (
                f"    {{UI_TEXT, {obj['x']}, {obj['y']}, "
                f"0, 0, {fill}, 0x0000, {font_size}, \"{text_val}\"}},\n"
            )

    # ============================================
    # generated_ui.h (UNCHANGED - Interface)
    # ============================================
    generated_ui_h = f"""#ifndef GENERATED_UI_H
#define GENERATED_UI_H

#include <stdint.h>

typedef enum {{
    UI_RECTANGLE,
    UI_OVAL,
    UI_TEXT
}} UI_ObjectType;

typedef struct {{
    UI_ObjectType type;
    int x;
    int y;
    int width;
    int height;
    uint16_t fill;
    uint16_t outline;
    int font_size;
    char text[50];
}} UI_Object;

#define UI_OBJECT_COUNT {len(ui_objects)}

extern UI_Object ui_objects[UI_OBJECT_COUNT];

#endif
"""

    # ============================================
    # generated_ui.c (UNCHANGED - Data)
    # ============================================
    generated_ui_c = f"""#include "generated_ui.h"

UI_Object ui_objects[UI_OBJECT_COUNT] = {{
{object_entries}}};
"""

    # ============================================
    # ui_renderer.h (STM32H7 OPTIMIZED)
    # ============================================
    ui_renderer_h = """#ifndef UI_RENDERER_H
#define UI_RENDERER_H

#include "generated_ui.h"
#include <stdint.h>

/* UI Rendering Backend Modes */
#define UI_RENDER_BACKEND_LCD      1
#define UI_RENDER_BACKEND_LTDC     2

/* Select LTDC for STM32H7 with hardware acceleration */
#define UI_RENDER_BACKEND UI_RENDER_BACKEND_LTDC

/* LTDC Configuration */
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC
#define LCD_WIDTH   480
#define LCD_HEIGHT  272
#define LCD_BYTES_PER_PIXEL 2  /* RGB565 format */
#endif

/* Main Rendering Functions */
void UI_Render(void);
void UI_RenderInit(void);
void UI_ClearBuffer(uint16_t color);
uint16_t* UI_GetFramebufferPtr(void);
uint32_t UI_GetFPS(void);

#endif
"""

    # ============================================
    # ui_renderer.c (STM32H7 LTDC + DMA2D)
    # ============================================
    ui_renderer_c = """#include "ui_renderer.h"
#include "ui_stm_integration.h"
#include "stm32h7xx_hal.h"
#include "ltdc.h"
#include "dma2d.h"

/* Framebuffer pointer to LTDC-configured address (0x24000000) */
#define FRAMEBUFFER_ADDR ((uint16_t *)0x24000000)
static uint16_t *framebuffer = FRAMEBUFFER_ADDR;

static uint32_t g_FrameCounter = 0;
static uint32_t g_LastFrameTime = 0;
static uint32_t g_FPS = 0;

/* Helper: Draw pixel to framebuffer */
static void draw_pixel(int x, int y, uint16_t color)
{
    if (x >= 0 && x < LCD_WIDTH && y >= 0 && y < LCD_HEIGHT)
        framebuffer[y * LCD_WIDTH + x] = color;
}

/* Helper: Draw filled rectangle (hardware accelerated if available) */
static void draw_filled_rect(int x, int y, int w, int h, uint16_t color)
{
    /* Clip to bounds */
    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (x + w > LCD_WIDTH) w = LCD_WIDTH - x;
    if (y + h > LCD_HEIGHT) h = LCD_HEIGHT - y;
    
    if (w <= 0 || h <= 0) return;

#ifdef STM32H7_DMA2D_ENABLE
    /* Use DMA2D for hardware acceleration */
    DMA2D_FillRect(x, y, w, h, color);
#else
    /* Software fallback */
    for (int py = y; py < y + h; py++) {
        for (int px = x; px < x + w; px++) {
            draw_pixel(px, py, color);
        }
    }
#endif
}

/* Helper: Draw rectangle outline */
static void draw_rect_outline(int x, int y, int w, int h, uint16_t color)
{
    draw_filled_rect(x, y, w, 1, color);                    /* Top */
    draw_filled_rect(x, y + h - 1, w, 1, color);            /* Bottom */
    draw_filled_rect(x, y, 1, h, color);                    /* Left */
    draw_filled_rect(x + w - 1, y, 1, h, color);            /* Right */
}

/* Helper: Draw filled ellipse/oval */
static void draw_filled_ellipse(int x, int y, int w, int h, uint16_t color)
{
    int x_center = x + w / 2;
    int y_center = y + h / 2;
    int a = w / 2;
    int b = h / 2;
    
    if (a <= 0 || b <= 0) return;
    
    int a2 = a * a;
    int b2 = b * b;
    int x_curr = 0;
    int y_curr = b;
    int d = b2 + a2 / 4 - a2 * b;
    
    while (x_curr * b2 < y_curr * a2) {
        for (int py = y_center - y_curr; py <= y_center + y_curr; py++) {
            draw_pixel(x_center + x_curr, py, color);
            if (x_curr > 0)
                draw_pixel(x_center - x_curr, py, color);
        }
        
        if (d < 0) {
            d = d + 2 * b2 * x_curr + b2;
        } else {
            d = d + 2 * b2 * x_curr - 2 * a2 * y_curr + b2;
            y_curr--;
        }
        x_curr++;
    }
}

void UI_ClearBuffer(uint16_t color)
{
    uint32_t *p32 = (uint32_t *)framebuffer;
    uint32_t color32 = (color << 16) | color;
    
    for (size_t i = 0; i < (LCD_WIDTH * LCD_HEIGHT / 2); i++) {
        p32[i] = color32;
    }
}

void UI_RenderInit(void)
{
    /* Initialize framebuffer and display system */
    UI_FramebufferInit();
    UI_ClearBuffer(0xFFFF);  /* Clear to white */
    g_LastFrameTime = HAL_GetTick();
    g_FrameCounter = 0;
}

void UI_Render(void)
{
    /* Clear framebuffer */
    UI_ClearBuffer(0xFFFF);  /* White background */
    
    /* Render all UI objects */
    for (int i = 0; i < UI_OBJECT_COUNT; i++) {
        UI_Object *obj = &ui_objects[i];
        
        switch (obj->type) {
            case UI_RECTANGLE:
                draw_filled_rect(obj->x, obj->y, obj->width, obj->height, obj->fill);
                if (obj->outline != 0x0000) {
                    draw_rect_outline(obj->x, obj->y, obj->width, obj->height, obj->outline);
                }
                break;
                
            case UI_OVAL:
                draw_filled_ellipse(obj->x, obj->y, obj->width, obj->height, obj->fill);
                break;
                
            case UI_TEXT:
                if (obj->text[0] != '\\0') {
                    /* Simple text rendering - can be enhanced */
                    UI_DrawText(obj->x, obj->y, obj->text, obj->fill, obj->font_size);
                }
                break;
                
            default:
                break;
        }
    }
    
    /* Update frame statistics */
    g_FrameCounter++;
    uint32_t now = HAL_GetTick();
    if (now - g_LastFrameTime >= 1000) {
        g_FPS = g_FrameCounter;
        g_FrameCounter = 0;
        g_LastFrameTime = now;
    }
}

uint16_t* UI_GetFramebufferPtr(void)
{
    return framebuffer;
}

uint32_t UI_GetFPS(void)
{
    return g_FPS;
}
"""

    # ============================================
    # ui_layout.c (Layout helper - unchanged)
    # ============================================
    ui_layout_c = """#include "generated_ui.h"

/* Layout utilities can be added here */
/* For example: auto-positioning, grid layout, etc. */
"""

    # ============================================
    # ui_stm_integration.h (Hardware Abstraction API)
    # ============================================
    ui_stm_integration_h = """/**
 * @file ui_stm_integration.h
 * @brief STM32 HAL Integration Layer for UI Rendering System
 * @details Provides hardware abstraction for LTDC display, DMA2D acceleration,
 *          and framebuffer management for STM32H7 series.
 * @date 2026
 */

#ifndef UI_STM_INTEGRATION_H
#define UI_STM_INTEGRATION_H

#include <stdint.h>
#include <stddef.h>

/* ===================================================================
    FRAMEBUFFER CONFIGURATION FOR STM32H7
    =================================================================== */

/* Define LTDC/LCD dimensions (reduced to fit in 320KB internal RAM) */
#define LTDC_WIDTH          480
#define LTDC_HEIGHT         272

/* RGB565 format: 2 bytes per pixel */
#define LTDC_BYTES_PER_PIXEL 2
#define LTDC_BUFFER_SIZE     (LTDC_WIDTH * LTDC_HEIGHT * LTDC_BYTES_PER_PIXEL)

/* Enable DMA2D hardware acceleration for fast rectangle fills */
#define STM32H7_DMA2D_ENABLE

/* Framebuffer locations - using internal AXI SRAM (D1 domain) */
/* 480x272x2 = 261KB fits within 320KB available in AXI SRAM */
#define INTERNAL_RAM_BASE    0x24000000  /* AXI SRAM D1 domain */
#define FRAMEBUFFER_LAYER0   ((uint16_t *)(INTERNAL_RAM_BASE))  /* Layer 0 */
#define FRAMEBUFFER_LAYER1   ((uint16_t *)(INTERNAL_RAM_BASE + 0x00040000))  /* Layer 1 (if using double buffering) */

/* Current configuration: 480x272x2 = 261KB fits in 320KB internal RAM */
/* For higher resolution (800x480 = 768KB), use external memory via OCTOSPI */

/* ===================================================================
    DMA2D HARDWARE ACCELERATION
    =================================================================== */

#ifdef STM32H7_DMA2D_ENABLE
/**
 * @brief Hardware-accelerated rectangle fill using DMA2D
 * @param x,y: Start coordinates
 * @param w,h: Width and height
 * @param color: RGB565 color value
 */
void DMA2D_FillRect(int x, int y, int w, int h, uint16_t color);

/**
 * @brief Wait for DMA2D operation to complete
 */
void DMA2D_WaitComplete(void);

#endif

/* ===================================================================
    FRAMEBUFFER OPERATIONS
    =================================================================== */

/**
 * @brief Initialize framebuffer and display hardware
 * Configures LTDC, DMA2D, and SDRAM for rendering
 */
void UI_FramebufferInit(void);

/**
 * @brief Clear entire framebuffer to color
 */
void UI_FramebufferClear(uint16_t color);

/**
 * @brief Swap framebuffers (double-buffering)
 * @note Requires configured LTDC interrupts
 */
void UI_FramebufferSwap(void);

/**
 * @brief Get current active framebuffer pointer
 */
uint16_t* UI_GetFramebuffer(void);

/**
 * @brief Write pixel to framebuffer
 * @param x,y: Pixel coordinates
 * @param color: RGB565 color
 */
static inline void UI_DrawPixel(int x, int y, uint16_t color)
{
     if (x >= 0 && x < LTDC_WIDTH && y >= 0 && y < LTDC_HEIGHT) {
          uint16_t *fb = UI_GetFramebuffer();
          fb[y * LTDC_WIDTH + x] = color;
     }
}

/* ===================================================================
    RENDERING FUNCTIONS (STM Hardware Optimized)
    =================================================================== */

/**
 * @brief Draw filled rectangle (hardware accelerated if available)
 */
void UI_DrawFilledRect(int x, int y, int w, int h, uint16_t color);

/**
 * @brief Draw rectangle outline
 */
void UI_DrawRectOutline(int x, int y, int w, int h, uint16_t color, int thickness);

/**
 * @brief Draw filled circle/oval (software implementation)
 */
void UI_DrawFilledOval(int x, int y, int w, int h, uint16_t color);

/**
 * @brief Draw text using system font
 * @param x,y: Top-left position
 * @param text: Null-terminated string
 * @param color: Text color (RGB565)
 * @param size: Font size (12, 16, 20, 24 supported)
 */
void UI_DrawText(int x, int y, const char *text, uint16_t color, int size);

/* ===================================================================
    UI RENDERING (Main Entry Point)
    =================================================================== */

/**
 * @brief Render entire UI from ui_objects array
 * Call this from main loop at desired frame rate (typically 30-60 FPS)
 */
void UI_RenderFrame(void);

/**
 * @brief Update display from framebuffer (LTDC refresh)
 * Called automatically by LTDC VSYNC interrupt
 */
void UI_DisplayUpdate(void);

/* ===================================================================
    UTILITIES
    =================================================================== */

/**
 * @brief Convert RGB888 color to RGB565 format
 */
uint16_t UI_RGB888_to_RGB565(uint8_t r, uint8_t g, uint8_t b);

/**
 * @brief Get tick counter for FPS/timing
 */
uint32_t UI_GetTicks(void);

#endif /* UI_STM_INTEGRATION_H */
"""

    # ============================================
    # ui_stm_integration.c (Hardware Abstraction)
    # ============================================
    ui_stm_integration_c = """/**
 * @file ui_stm_integration.c
 * @brief STM32 Hardware Integration for UI Rendering
 * @details LTDC, DMA2D, framebuffer management implementation
 */

#include "ui_stm_integration.h"
#include "generated_ui.h"
#include "stm32h7xx_hal.h"
#include "ltdc.h"
#include "dma2d.h"

/* ===================================================================
   FRAMEBUFFER STATE
   =================================================================== */

static uint16_t *g_pFramebuffer = FRAMEBUFFER_LAYER0;
/* Note: Double buffering disabled due to memory constraints */

/* ===================================================================
   FRAMEBUFFER OPERATIONS
   =================================================================== */

void UI_FramebufferInit(void)
{
    /* Framebuffers configured by STM32CubeMX during MX_LTDC_Init() */
    /* Using internal AXI SRAM for framebuffer */
    
    g_pFramebuffer = FRAMEBUFFER_LAYER0;
    
    /* Clear buffer */
    UI_FramebufferClear(0x0000);  /* Black */
}

void UI_FramebufferClear(uint16_t color)
{
    uint32_t *p32 = (uint32_t *)g_pFramebuffer;
    uint32_t color32 = (color << 16) | color;  /* Pack two pixels as 32-bit value */
    
    /* Clear by 32-bit writes (faster) */
    for (size_t i = 0; i < LTDC_BUFFER_SIZE / 4; i++) {
        p32[i] = color32;
    }
}

void UI_FramebufferSwap(void)
{
    /* Double buffering not available due to memory constraints */
    /* Single buffer mode only */
}

uint16_t* UI_GetFramebuffer(void)
{
    return g_pFramebuffer;
}

/* ===================================================================
   DMA2D HARDWARE ACCELERATION
   =================================================================== */

#ifdef STM32H7_DMA2D_ENABLE

void DMA2D_FillRect(int x, int y, int w, int h, uint16_t color)
{
    /* Clip to framebuffer bounds */
    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (x + w > LTDC_WIDTH) w = LTDC_WIDTH - x;
    if (y + h > LTDC_HEIGHT) h = LTDC_HEIGHT - y;
    
    if (w <= 0 || h <= 0) return;
    
    /* Calculate start address in framebuffer */
    uint32_t start_addr = (uint32_t)g_pFramebuffer + (y * LTDC_WIDTH + x) * 2;
    
    /* Configure DMA2D for memory fill operation */
    DMA2D_HandleTypeDef hdma2d;
    hdma2d.Instance = DMA2D;
    
    /* Memset operation: fill rectangle with single color */
    if (HAL_DMA2D_Start(&hdma2d, color, start_addr, w, h) != HAL_OK) {
        /* Fallback to software if DMA2D fails */
        for (int py = y; py < y + h; py++) {
            for (int px = x; px < x + w; px++) {
                UI_DrawPixel(px, py, color);
            }
        }
    }
}

void DMA2D_WaitComplete(void)
{
    /* Wait for DMA2D to complete current operation */
    while (DMA2D->CR & DMA2D_CR_START) {
        /* Poll until complete */
    }
}

#endif

/* ===================================================================
   RENDERING PRIMITIVES
   =================================================================== */

void UI_DrawFilledRect(int x, int y, int w, int h, uint16_t color)
{
#ifdef STM32H7_DMA2D_ENABLE
    /* Use hardware DMA2D acceleration if available */
    DMA2D_FillRect(x, y, w, h, color);
#else
    /* Software implementation */
    for (int py = y; py < y + h; py++) {
        for (int px = x; px < x + w; px++) {
            UI_DrawPixel(px, py, color);
        }
    }
#endif
}

void UI_DrawRectOutline(int x, int y, int w, int h, uint16_t color, int thickness)
{
    /* Top line */
    UI_DrawFilledRect(x, y, w, thickness, color);
    /* Bottom line */
    UI_DrawFilledRect(x, y + h - thickness, w, thickness, color);
    /* Left line */
    UI_DrawFilledRect(x, y, thickness, h, color);
    /* Right line */
    UI_DrawFilledRect(x + w - thickness, y, thickness, h, color);
}

void UI_DrawFilledOval(int x, int y, int w, int h, uint16_t color)
{
    /* Midpoint ellipse algorithm */
    int x_center = x + w / 2;
    int y_center = y + h / 2;
    int a = w / 2;  /* semi-major axis */
    int b = h / 2;  /* semi-minor axis */
    
    if (a <= 0 || b <= 0) return;
    
    int a2 = a * a;
    int b2 = b * b;
    int x_curr = 0;
    int y_curr = b;
    int d = b2 + a2 / 4 - a2 * b;
    
    while (x_curr * b2 < y_curr * a2) {
        /* Draw horizontal line at y */
        UI_DrawFilledRect(x_center - x_curr, y_center + y_curr, 2 * x_curr, 1, color);
        UI_DrawFilledRect(x_center - x_curr, y_center - y_curr, 2 * x_curr, 1, color);
        
        if (d < 0) {
            d = d + 2 * b2 * x_curr + b2;
        } else {
            d = d + 2 * b2 * x_curr - 2 * a2 * y_curr + b2;
            y_curr--;
        }
        x_curr++;
    }
}

/* ===================================================================
   TEXT RENDERING (Simple System Font)
   =================================================================== */

/* Simple 5x7 bitmap font (ASCII 32-126) */
static const uint8_t g_FontData5x7[] = {
    0x00, 0x00, 0x00, 0x00, 0x00,  /* Space */
    0x3E, 0x5B, 0x4F, 0x59, 0x3E,  /* @ */
    /* Additional fonts can be added here */
};

void UI_DrawText(int x, int y, const char *text, uint16_t color, int size)
{
    if (!text) return;
    
    /* Simple text rendering: draw each character as a block */
    int char_width = 6 * size / 12;
    int char_height = 8 * size / 12;
    
    int x_pos = x;
    /* IMPORTANT: Use proper escape sequences: \\0 for null terminator, \\n for newline */
    for (const char *c = text; *c != '\\0'; c++) {
        if (*c == '\\n') {
            x_pos = x;
            y += char_height;
        } else {
            /* Draw character as rectangle (placeholder) */
            UI_DrawFilledRect(x_pos, y, char_width, char_height, color);
            x_pos += char_width;
        }
    }
}

/* ===================================================================
   UI RENDERING MAIN FUNCTION
   =================================================================== */

void UI_RenderFrame(void)
{
    /* Clear framebuffer */
    UI_FramebufferClear(0xFFFF);  /* White background */
    
    /* Render all UI objects from generated_ui.c */
    for (int i = 0; i < UI_OBJECT_COUNT; i++) {
        UI_Object *obj = &ui_objects[i];
        
        switch (obj->type) {
            case UI_RECTANGLE:
                UI_DrawFilledRect(obj->x, obj->y, obj->width, obj->height, obj->fill);
                UI_DrawRectOutline(obj->x, obj->y, obj->width, obj->height, obj->outline, 1);
                break;
                
            case UI_OVAL:
                UI_DrawFilledOval(obj->x, obj->y, obj->width, obj->height, obj->fill);
                /* Outline would require ellipse algorithm */
                break;
                
            case UI_TEXT:
                UI_DrawText(obj->x, obj->y, obj->text, obj->fill, obj->font_size);
                break;
                
            default:
                break;
        }
    }
    
    /* Update display */
    UI_DisplayUpdate();
}

void UI_DisplayUpdate(void)
{
    /* Typically called by LTDC VSYNC interrupt for automatic refresh */
    /* Or can be called explicitly to force update */
    
    #ifdef STM32H7xx
    /* Update LTDC layer framebuffer address if needed */
    /* This is handled by the LTDC driver configuration */
    #endif
}

/* ===================================================================
   UTILITY FUNCTIONS
   =================================================================== */

uint16_t UI_RGB888_to_RGB565(uint8_t r, uint8_t g, uint8_t b)
{
    /* Convert 8-bit RGB to 5-6-5 format */
    uint16_t rgb565 = (
        ((r & 0xF8) << 8) |   /* R: bits 15-11 */
        ((g & 0xFC) << 3) |   /* G: bits 10-5 */
        ((b & 0xF8) >> 3)     /* B: bits 4-0 */
    );
    return rgb565;
}

uint32_t UI_GetTicks(void)
{
    return HAL_GetTick();
}
"""

    # ============================================
    # linker_sdram_config.h (Configuration Guide)
    # ============================================
    linker_sdram_config_h = """/**
 * @file linker_sdram_config.h
 * @brief STM32H7 SDRAM Linker Script Configuration Guide
 * 
 * This file explains how to configure the linker script for framebuffer placement
 * in SDRAM, which is required for the UI rendering system.
 */

/*
================================================================================
LINKER SCRIPT MODIFICATIONS FOR STM32H7 SDRAM FRAMEBUFFER
================================================================================

The UI rendering system uses a framebuffer placed in SDRAM for efficient rendering.
Follow these steps to properly configure your linker script:

1. MEMORY SECTION MODIFICATION
================================
Add/modify the MEMORY section in your .ld file:

MEMORY
{
    DTCMRAM (xrw)   : ORIGIN = 0x20000000, LENGTH = 128K
    RAM (xrw)       : ORIGIN = 0x20020000, LENGTH = 384K
    ITCMRAM (xrw)   : ORIGIN = 0x00000000, LENGTH = 64K
    FLASH (rx)      : ORIGIN = 0x08000000, LENGTH = 2048K
    SDRAM (xrw)     : ORIGIN = 0xC0000000, LENGTH = 32M    /* FMC SDRAM */
}

2. SECTIONS MODIFICATION
=========================
Add the following section to place framebuffer in SDRAM:

/* SDRAM section for framebuffer */
.sdram (NOLOAD) :
{
    . = ALIGN(4);
    _sdram_start = .;
    *(SORT(.sdram*))
    . = ALIGN(4);
    _sdram_end = .;
} > SDRAM AT > SDRAM

Place this section BEFORE the closing brace of SECTIONS { ... }

3. INITIALIZATION CODE
=======================
Ensure your startup code initializes SDRAM before using the framebuffer:

In SystemInit() or similar startup function, initialize the FMC SDRAM controller:
- Configure GPIO for SDRAM signals
- Configure FMC memory interface
- Configure SDRAM timing parameters
- Send initialization commands to SDRAM

This is typically done by STMCubeMX-generated code in the system setup.

4. FRAMEBUFFER PLACEMENT
=========================
With the linker script configured, declare framebuffer as:

__attribute__((section(".sdram")))
uint16_t framebuffer[LCD_WIDTH * LCD_HEIGHT];

The linker will automatically place this in SDRAM.

5. CACHE CONSIDERATIONS
========================
For STM32H7 with data cache, consider:

- Disable caching for SDRAM region (if using hardware cache)
- Or properly manage cache coherency when updating framebuffer
- Use __DSB() and __ISB() barriers when needed

Example cache disable:
    SCB->DACR = 0;  // Disable data cache completely
    Or use MPU to disable caching for SDRAM region only

================================================================================
*/

/* Memory layout for reference:
     0x00000000 - 0x0000FFFF  : ITCM-RAM (64 KB)   - Code cache
     0x20000000 - 0x2001FFFF  : DTCM-RAM (128 KB)  - Data cache
     0x20020000 - 0x2007FFFF  : RAM (384 KB)       - Main RAM
     0x08000000 onward        : Flash              - Program storage
     0x24000000 - 0x2404FFFF  : AXI SRAM (320 KB)  - Framebuffer location
   
     Current framebuffer: 0x24000000 (AXI SRAM D1 domain)
     Size for 480x272 RGB565: 480 * 272 * 2 = 261 KB (fits in 320KB)
*/
"""

    # ============================================
    # INTEGRATION_NOTES.md (Documentation)
    # ============================================
    integration_notes = """# UI Code Integration Guide for STM32H7

## Files Generated
- `generated_ui.h/c` - UI object definitions (DO NOT MODIFY)
- `ui_renderer.h/c` - STM32H7 rendering engine (optimized for LTDC + DMA2D)
- `ui_layout.c` - Layout utilities for future expansion

## Integration Steps

### 1. Copy Files to STM32 Project
Files are automatically generated in your project's Display folder:
```
UI_Integration/
└── Display/
    ├── Inc/
    │   ├── generated_ui.h
    │   ├── ui_renderer.h
    │   ├── ui_stm_integration.h
    │   └── linker_sdram_config.h (Reference)
    └── Src/
        ├── generated_ui.c
        ├── ui_renderer.c
        ├── ui_stm_integration.c
        └── ui_layout.c
```

### 2. STM32CubeIDE Build Configuration
Ensure Display folder is included in build paths:
- Right-click project → Properties → C/C++ Build → Settings
- Add to Include Paths: `"${workspace_loc:/${ProjName}/Display/Inc}"`
- Verify in .cproject that Display/Src is in source entries

### 3. Framebuffer Configuration (Already Done)
The framebuffer uses internal AXI SRAM at 0x24000000:
- Resolution: 480x272 RGB565 (261 KB)
- Fits in 320KB AXI SRAM D1 domain
- LTDC configured in Core/Src/ltdc.c
- No external SDRAM required

### 4. Update main.c (If Not Already Done)
Add these includes and initialization:
```c
/* USER CODE BEGIN Includes */
#include "ui_renderer.h"
#include "ui_stm_integration.h"
/* USER CODE END Includes */

/* In initialization section (USER CODE BEGIN 2) */
UI_RenderInit();

/* In main loop (USER CODE BEGIN WHILE) */
while (1) {
    UI_Render();
    HAL_Delay(16);  /* ~60 FPS */
    /* USER CODE END WHILE */
}
```

### 5. Build Configuration
- Ensure STM32CubeMX has LTDC and DMA2D initialized
- LTDC Layer 0 must point to 0x24000000 with RGB565 format

### 6. Display Backend Selection
In `ui_renderer.h`, select rendering backend:
- `UI_RENDER_BACKEND_LCD` - For external LCD driver
- `UI_RENDER_BACKEND_LTDC` - For STM32 LTDC controller (RECOMMENDED)

### 7. Hardware Acceleration (Optional)
DMA2D acceleration is enabled by default when using LTDC.
Disable in `ui_stm_integration.h` if needed:
```c
/* Comment out to disable DMA2D */
#define STM32H7_DMA2D_ENABLE
```

## UI Object Properties

### Position & Size
- `x, y` - Top-left corner coordinates
- `width, height` - Dimensions in pixels

### Colors (RGB565 16-bit format)
- `fill` - Fill color (0xRRGGBBB in RGB565)
- `outline` - Border color

### Text Properties  
- `font_size` - Size in pixels (12, 16, 20, 24)
- `text` - Text string (up to 50 characters)

## Example Usage

Modify UI objects at runtime:
```c
/* Change rectangle color */
ui_objects[0].fill = UI_RGB888_to_RGB565(255, 0, 0);  /* Red */

/* Change text */
strcpy(ui_objects[1].text, "New Text");

/* Trigger re-render */
UI_Render();
```

## Performance Tips

1. **FPS Monitoring**
   - Call `UI_GetFPS()` to get framerate
   - Adjust `HAL_Delay(16)` for different target FPS

2. **DMA2D Acceleration**
   - Rectangle fills use hardware DMA2D
   - Much faster than software rendering
   - Ensure DMA2D is initialized by STMCubeMX

3. **Framebuffer Location**
   - Located in internal AXI SRAM (0x24000000)
   - 480x272 RGB565 = 261 KB (fits in 320KB RAM)
   - For higher resolutions, external memory required

## Troubleshooting

**Display shows garbage:**
- Check SDRAM initialization
- Verify framebuffer address in linker script
- Ensure MX_LTDC_Init() called before UI_RenderInit()

**Build errors:**
- Verify all includes are in include paths
- Check STM32CubeMX has generated ltdc.h, dma2d.h
- Ensure linker script has SDRAM section

**Rendering too slow:**
- Disable DMA2D and check framebuffer clearing speed
- Check if SDRAM bandwidth is bottleneck
- Consider using partial updates instead of full refresh

## Future Enhancements

- Multi-layer rendering
- Partial screen updates
- Animation framework
- Widget library (buttons, sliders, etc.)
- Touch input handling
"""

    # ============================================
    # SAVE FILES
    # ============================================
    # ============================================
    # SAVE FILES (with UTF-8 encoding)
    # ============================================
    try:
        with open(os.path.join(inc_path, "generated_ui.h"), "w", encoding='utf-8') as f:
            f.write(generated_ui_h)

        with open(os.path.join(src_path, "generated_ui.c"), "w", encoding='utf-8') as f:
            f.write(generated_ui_c)

        with open(os.path.join(inc_path, "ui_renderer.h"), "w", encoding='utf-8') as f:
            f.write(ui_renderer_h)

        with open(os.path.join(src_path, "ui_renderer.c"), "w", encoding='utf-8') as f:
            f.write(ui_renderer_c)
            
        with open(os.path.join(src_path, "ui_layout.c"), "w", encoding='utf-8') as f:
            f.write(ui_layout_c)
        
        # STM Integration Files - NOW AUTO-GENERATED
        with open(os.path.join(inc_path, "ui_stm_integration.h"), "w", encoding='utf-8') as f:
            f.write(ui_stm_integration_h)
        
        with open(os.path.join(src_path, "ui_stm_integration.c"), "w", encoding='utf-8') as f:
            f.write(ui_stm_integration_c)
        
        with open(os.path.join(inc_path, "linker_sdram_config.h"), "w", encoding='utf-8') as f:
            f.write(linker_sdram_config_h)
            
        with open(os.path.join(current_project_path, "INTEGRATION_NOTES.md"), "w", encoding='utf-8') as f:
            f.write(integration_notes)

        messagebox.showinfo(
            "Success",
            "✅ STM32H7 UI Code Generated Successfully!\\n\\n"
            "📁 Generated Files:\\n"
            "  ✨ ui_stm_integration.h/c (Hardware abstraction)\\n"
            "  • generated_ui.h/c (UI object definitions)\\n"
            "  • ui_renderer.h/c (STM32H7 optimized rendering)\\n"
            "  • ui_layout.c (Layout utilities)\\n"
            "  📋 linker_sdram_config.h (Linker script guide)\\n"
            "  • INTEGRATION_NOTES.md (Integration guide)\\n\\n"
            "⚙️ Hardware Features:\\n"
            "  • LTDC display output\\n"
            "  • DMA2D hardware acceleration\\n"
            "  • Internal AXI SRAM framebuffer (480x272)\\n\\n"
            "🎉 Next steps:\\n"
            "  1. All files ready in Display/Inc/ and Display/Src/\\n"
            "  2. Rebuild project in STM32CubeIDE\\n"
            "  3. Flash and test"
        )

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate files:\\n{e}")

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