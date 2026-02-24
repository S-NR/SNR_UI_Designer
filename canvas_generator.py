import tkinter as tk
from tkinter import messagebox

PADDING = 100  # 100px on each side

def create_canvas():
    try:
        ui_width = int(width_entry.get())
        ui_height = int(height_entry.get())

        canvas_width = ui_width + (PADDING * 2)
        canvas_height = ui_height + (PADDING * 2)

        # New window
        canvas_window = tk.Toplevel(root)
        canvas_window.title("Canvas With UI Layout")
        canvas_window.geometry(f"{canvas_width}x{canvas_height}")

        canvas = tk.Canvas(
            canvas_window,
            width=canvas_width,
            height=canvas_height,
            bg="lightgray"
        )
        canvas.pack()

        # Draw UI layout area (centered)
        canvas.create_rectangle(
            PADDING,
            PADDING,
            PADDING + ui_width,
            PADDING + ui_height,
            fill="white",
            outline="black",
            width=2
        )

        # Optional label
        canvas.create_text(
            canvas_width // 2,
            30,
            text="Canvas Area (Gray) with UI Layout (White)",
            font=("Arial", 12, "bold")
        )

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers")

# Main window
root = tk.Tk()
root.title("Canvas Creator")
root.geometry("300x200")

tk.Label(root, text="Enter UI Width:").pack(pady=5)
width_entry = tk.Entry(root)
width_entry.pack()

tk.Label(root, text="Enter UI Height:").pack(pady=5)
height_entry = tk.Entry(root)
height_entry.pack()

tk.Button(root, text="Create Canvas", command=create_canvas).pack(pady=15)

root.mainloop()