import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

PADDING = 100
ui_objects = []
current_project_name = None
current_project_path = None

def start_new_project():
    global current_project_name, current_project_path

    # 1️⃣ Ask Project Name
    project_name = simpledialog.askstring("Project Name", "Enter your project name:")
    if not project_name:
        messagebox.showwarning("Cancelled", "Project creation cancelled!")
        return False
    current_project_name = project_name

    # 2️⃣ Ask Project Path
    project_path = filedialog.askdirectory(title="Select folder to save your project")
    if not project_path:
        messagebox.showwarning("Cancelled", "Project creation cancelled!")
        return False
    current_project_path = project_path

    return True

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

def launch_builder_flow():
    """
    Startup sequence: Project Name -> Path -> Dimensions -> Canvas
    """
    if start_new_project():
        create_ui_dimensions_window()


# ================================
# Main Start Window
# ================================
root = tk.Tk()
root.title("Start New UI Project")
root.geometry("300x150")

tk.Label(root, text="Start a new UI Project").pack(pady=20)
tk.Button(root, text="Create New Project", command=launch_builder_flow).pack(pady=10)

root.mainloop()