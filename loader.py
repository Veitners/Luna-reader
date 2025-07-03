import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import plotter as plot
import processing as util
def load_file(app):
    """Load file and show loading window."""
    master = app.master
    loading_window = tk.Toplevel(master)
    loading_window.title("Loading")
    loading_window.geometry("300x100")
    filepath = filedialog.askopenfilename(filetypes=[("TSV files", "*.tsv")])
    if not filepath:
        loading_window.destroy()
        return

    try:
        df = pd.read_csv(filepath, sep='\t', header=None, skiprows=31, engine='python')
        df = df.astype(str)
        x_axis_row = util.find_x_axis_row(df)
        if x_axis_row is None:
            messagebox.showerror(
                "Error",
                "No 'x-axis' cell found in the file."
            )
            loading_window.destroy()
            return

    except (pd.errors.ParserError, FileNotFoundError, OSError, ValueError) as e:
        messagebox.showerror(
            "Error",
            f"Failed to load file: {e}"
        )
        loading_window.destroy()
        return
    finally:
        loading_window.destroy()

    if df.shape[0] < 2 or df.shape[1] < 2:
        messagebox.showerror(
            "Error",
            "Data does not have enough rows or columns to plot."
        )
        return

    df = df.astype(str)
    tare_cells = df.iloc[:x_axis_row, :].apply(
        lambda row: row.str.contains('Tare', case=False, na=False)
    ).stack()
    tare_options = [
        (idx[0] + 1, idx[1] + 1)
        for idx, value in tare_cells.items() if value
    ]

    tare_values = None
    tare_dropdown = None

    if tare_options:
        tare_values = df.iloc[
            [row - 1 for row, _ in tare_options], 3:
        ].apply(
            pd.to_numeric, errors='coerce'
        ).values

        if hasattr(app, "tare_dropdown") and app.tare_dropdown is not None:
            app.tare_dropdown.destroy()
            app.tare_dropdown = None

        tare_var = tk.StringVar(
            value=f"Row {tare_options[0][0]}, Column {tare_options[0][1]}"
        )
        tare_dropdown = tk.OptionMenu(
            app.zeroing_frame,
            tare_var,
            *[f"Row {row}, Column {col}" for row, col in tare_options]
        )
        tare_dropdown.pack(side=tk.LEFT, padx=5)
        app.tare_dropdown = tare_dropdown

        def confirm_tare_selection(*args):
            selected_option = tare_var.get()
            selected_row = int(
                selected_option.split()[1].strip(',')
            )
            app.tare = tare_values[selected_row - 1]

        tare_var.trace("w", confirm_tare_selection)
        app.tare = tare_values[0]
        app.tare_values = tare_values
    else:
        messagebox.showinfo("Info", "No 'Tare' cells found above the 'x-axis' cell.")
        app.tare_values = None
        app.tare = None

    app.timestamps = df.iloc[x_axis_row + 1:, 0].values
    app.distances = pd.to_numeric(
        df.iloc[x_axis_row, 3:].values,
        errors='coerce'
    )
    app.original_data = df.iloc[
        x_axis_row + 1:,
        3:
    ].apply(pd.to_numeric, errors='coerce').values
    app.data = app.original_data.copy()
    app.current_timestamp_idx = 0

    app.slider.config(from_=0, to=len(app.data) - 1)
    app.slider.set(0)

    app.update_stats()
    app.plot_deformation = plot.plot_deformation
    app.plot_deformation(app)

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.readlines()[:30]
            app.data_text.config(state=tk.NORMAL)
            app.data_text.delete(1.0, tk.END)
            app.data_text.insert(tk.END, "".join(lines))
            app.data_text.config(state=tk.DISABLED)
    except (OSError, IOError) as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")
def load_csv_file(self):
    """Load CSV with point coordinates and plot them."""
    csv_file_path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")]
    )
    if not csv_file_path:
        messagebox.showerror(
            "Error",
            "No CSV file selected."
        )
        return
    plot.plot_point(self, csv_file_path)