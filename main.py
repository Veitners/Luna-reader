"""
Author: Edgars Veitners
"""
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk  # Import ttk for widgets like Progressbar
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

class DeformationApp:
    """Main application class for viewing"""
    def __init__(self, root):
        self.master = root
        self.master.title("Deformation over Distance Viewer")

        # Configure grid layout for resizing
        master = self.master
        master.rowconfigure(0, weight=0)  # Load frame
        master.rowconfigure(1, weight=0)  # Zeroing frame
        master.rowconfigure(2, weight=0)  # Playback controls
        master.rowconfigure(3, weight=0)  # Lock and reset buttons
        master.rowconfigure(4, weight=0)  # Slider
        master.rowconfigure(5, weight=1)  # Plot area
        master.rowconfigure(6, weight=0)  # Toolbar
        master.rowconfigure(7, weight=0)  # Stats frame
        master.columnconfigure(0, weight=1)

        # Frame to hold the load button and file label
        self.load_frame = tk.Frame(master)
        self.load_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=5)
        self.load_frame.columnconfigure(
            0,
            weight=1)

        # Button to open file
        self.load_button = tk.Button(
            self.load_frame,
            text="Open .tsv File",
            command=self.load_file
        )
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Button to load the CSV file
        self.load_csv_button = tk.Button(
            self.load_frame,
            text="Load XY CSV",
            command=self.load_csv_file,
            state="disabled"
        )
        self.load_csv_button.pack(
            side=tk.LEFT,
            padx=5
            )
        # Label to display the loaded file name
        self.file_label = tk.Label(
            self.load_frame,
            text="No file loaded",
            fg="gray"
        )
        self.file_label.pack(
            side=tk.LEFT,
            padx=5
            )

        # Frame to group zeroing-related buttons
        self.zeroing_frame = tk.LabelFrame(
            master,
            text="Zeroing Options",
            padx=10,
            pady=10
        )
        self.zeroing_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=10,
            pady=5
            )
        self.zeroing_frame.columnconfigure(
            0,
            weight=1
            )

        # Button to toggle zeroing
        self.zeroing_button = tk.Button(
            self.zeroing_frame,
            text="Toggle Zeroing",
            command=self.toggle_zeroing
        )
        self.zeroing_button.pack(side=tk.LEFT, padx=5)

        # Button to zero data from the selected timestamp
        self.zero_from_timestamp_button = tk.Button(
            self.zeroing_frame,
            text="Zero from Timestamp",
            command=self.zero_from_timestamp
        )
        self.zero_from_timestamp_button.pack(
            side=tk.LEFT,
            padx=5
            )

        # Button to add a new range
        self.add_range_button = tk.Button(
            self.zeroing_frame,
            text="Add Range",
            command=self.add_range
        )
        self.add_range_button.pack(side=tk.LEFT, padx=5)

        # Zeroing state
        self.zeroing_enabled = False

        # Frame to hold playback controls (moved above the slider)
        self.playback_frame = tk.Frame(master)
        self.playback_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=10,
            pady=5
        )
        self.playback_frame.columnconfigure(0, weight=1)

        # Frame to hold the lock, reset, and playback buttons
        self.button_frame = tk.Frame(master)
        self.button_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=10,
            pady=5
        )

        # Button to reset the graph
        self.reset_button = tk.Button(
            self.button_frame,
            text="Reset Graph",
            command=self.reset_graph
        )
        self.reset_button.pack(side=tk.RIGHT, padx=5)

        # Button to lock the current line
        self.lock_button = tk.Button(
            self.button_frame,
            text="Lock Line",
            command=self.lock_line
        )
        self.lock_button.pack(side=tk.RIGHT, padx=5)

        # Play/Pause toggle button
        self.play_pause_button = tk.Button(
            self.button_frame,
            text="⏯",
            command=self.toggle_playback
        )
        self.play_pause_button.pack(side=tk.LEFT, padx=5)

        # Fast Forward button
        self.fast_forward_button = tk.Button(
            self.button_frame,
            text="⏩",
            command=self.fast_forward
        )
        self.fast_forward_button.pack(side=tk.LEFT, padx=5)

        # Reverse button
        self.reverse_button = tk.Button(
            self.button_frame,
            text="⏪",
            command=self.reverse
        )
        self.reverse_button.pack(side=tk.LEFT, padx=5)

        # Frame to hold the slider and its label
        self.slider_frame = tk.Frame(master)
        self.slider_frame.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=10,
            pady=5)
        self.slider_frame.columnconfigure(0, weight=1)
        # Slider for navigation
        self.slider = tk.Scale(
            self.slider_frame,
            from_=0,
            to=0,
            orient=tk.HORIZONTAL,
            command=self.update_timestamp,
            length=700
        )
        self.slider.pack(side=tk.LEFT, padx=5)

        # Label to display the current timestamp index
        self.slider_label = tk.Label(
            self.slider_frame,
            text="Timestamp Index: 0"
        )
        self.slider_label.pack(side=tk.LEFT, padx=5)

        # List to store locked lines
        self.locked_lines = []

        # Frame to display the first rows of the .tsv file (spanning from top to bottom)
        self.data_frame = tk.Frame(master)
        self.data_frame.grid(row=0, column=1, rowspan=6, sticky="ns", padx=10, pady=5)
        self.data_frame.columnconfigure(0, weight=1)

        # Add a scrollbar for the data display
        self.data_scrollbar = tk.Scrollbar(self.data_frame, orient=tk.VERTICAL)
        self.data_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Text widget to display the data (read-only)
        self.data_text = tk.Text(
            self.data_frame,
            wrap=tk.NONE,
            yscrollcommand=self.data_scrollbar.set,
            width=40,
            state=tk.DISABLED
        )
        self.data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.data_scrollbar.config(command=self.data_text.yview)

        # Placeholder for the figure (adjusted to column 0)
        self.figure = plt.Figure(figsize=(8, 6))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas.get_tk_widget().grid(
            row=5,
            column=0,
            sticky="nsew",
            padx=10,
            pady=5
        )

        # Frame to hold the toolbar
        self.toolbar_frame = tk.Frame(master)
        self.toolbar_frame.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=10,
            pady=5
        )
        self.toolbar_frame.columnconfigure(0, weight=1)

        # Add Matplotlib's navigation toolbar for zoom and pan
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

        # Configure resizing for the canvas
        master.rowconfigure(5, weight=1)

        # Frame to display deformation statistics
        self.stats_frame = tk.Frame(master)
        self.stats_frame.grid(row=7, column=0, sticky="ew", padx=10, pady=5)
        self.stats_frame.columnconfigure(0, weight=1)

        # Labels for statistics
        self.peak_label = tk.Label(
            self.stats_frame,
            text="Peak Deformation: N/A"
        )
        self.peak_label.pack(side=tk.LEFT, padx=5)

        self.avg_label = tk.Label(
            self.stats_frame,
            text="Average Deformation: N/A"
        )
        self.avg_label.pack(side=tk.LEFT, padx=5)

        self.timestamp_label = tk.Label(
            self.stats_frame,
            text="Timestamp: N/A"
        )
        self.timestamp_label.pack(side=tk.LEFT, padx=5)

        self.position_label = tk.Label(
            self.stats_frame,
            text="Slider Position: 0"
        )
        self.position_label.pack(side=tk.LEFT, padx=5)

        # Playback state
        self.playback_speed = 1  # 1 for normal, >1 for fast forward, <0 for reverse
        self.playback_running = False

        # Maximum playback speed
        self.max_playback_speed = 8

        # Data holders
        self.data = None
        self.timestamps = None
        self.distances = None
        self.current_timestamp_idx = 0
        self.original_data = None  # Initialize original_data to avoid pylint error

        # Enable interactive mode for tooltips
        self.figure.canvas.mpl_connect("motion_notify_event", self.on_hover)

        # Initialize tare attribute
        self.tare = None
        # Initialize tare_values attribute
        self.tare_values = None

        # Initialize plot_window attribute to avoid attribute errors
        self.plot_window = None
        # Initialize colorbar attribute to avoid attribute errors
        self.colorbar = None
        # Initialize current_plot_data attribute to avoid attribute errors
        self.current_plot_data = []
        # Initialize tare_dropdown to avoid attribute errors
        self.tare_dropdown = None

    def find_x_axis_row(self, df):
        """Find the row and column index of the cell containing 'x-axis'."""
        # Ensure all values are strings to avoid errors with .str accessor
        df = df.astype(str)
        x_axis_cell = df.apply(lambda row: row.str.contains('x-axis', case=False, na=False)).stack()
        if not x_axis_cell.empty:
            # Returns (row, column) of the first match
            x_axis_row, x_axis_col = x_axis_cell.idxmax()
            return x_axis_row, x_axis_col
        else:
            return None

    def show_loading_window(self, message):
        """Displays a loading window with a progress bar."""
        loading_window = tk.Toplevel(self.master)
        loading_window.title("Loading")
        loading_window.geometry("300x100")
        loading_window.resizable(False, False)

        # Center the loading window
        self.center_window(loading_window)

        tk.Label(loading_window, text=message).pack(pady=10)

        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(
            loading_window,
            orient="horizontal",
            length=250,
            mode="determinate",
            variable=progress_var)
        progress_bar.pack(pady=10)

        return loading_window, progress_var

    def load_file(self):
        """Loads a .tsv file and processes it for plotting."""	
        filepath = filedialog.askopenfilename(filetypes=[("TSV files", "*.tsv")])
        if filepath:
            loading_window, progress = self.show_loading_window("Loading file...")
            try:
                # Simulate progress
                progress.set(10)
                self.master.update_idletasks()

                # Read .tsv file starting from line 31, skipping problematic rows
                df = pd.read_csv(filepath, sep='\t', header=None, skiprows=31, engine='python')

                progress.set(50)
                self.master.update_idletasks()
                # Ensure all values are strings before finding 'x-axis'
                df = df.astype(str)
                # Find the row and column index of the cell containing 'x-axis'
                x_axis_row, _ = self.find_x_axis_row(df)
                if x_axis_row is None:
                    messagebox.showerror(
                        "Error",
                        "No 'x-axis' cell found in the file."
                    )
                    loading_window.destroy()
                    return

                progress.set(100)
                self.master.update_idletasks()
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
            # Convert all values to strings to avoid TypeError
            df = df.astype(str)
            # Find all cells above x_axis_cell containing 'Tare'
            tare_cells = df.iloc[:x_axis_row, :].apply(
                lambda row: row.str.contains('Tare', case=False, na=False)
            ).stack()
            tare_options = [
                (idx[0] + 1, idx[1] + 1)
                for idx, value in tare_cells.items() if value
            ]

            if tare_options:
                # Store all tare rows as a 2D array
                self.tare_values = df.iloc[
                    [row - 1 for row, _ in tare_options], 3:
                ].apply(
                    pd.to_numeric, errors='coerce'
                ).values

                # Remove previous tare dropdown if it exists
                if hasattr(self, "tare_dropdown") and self.tare_dropdown is not None:
                    self.tare_dropdown.destroy()
                    self.tare_dropdown = None

                # Create a dropdown menu to select a Tare row
                tare_var = tk.StringVar(
                    value=f"Row {tare_options[0][0]}, Column {tare_options[0][1]}"
                )
                self.tare_dropdown = tk.OptionMenu(
                    self.zeroing_frame,
                    tare_var,
                    *[f"Row {row}, Column {col}" for row, col in tare_options]
                )
                self.tare_dropdown.pack(side=tk.LEFT, padx=5)

                def confirm_tare_selection():
                    selected_option = tare_var.get()
                    selected_row = int(
                        selected_option.split()[1].strip(',')
                    )
                    # Update tare to the selected row
                    self.tare = self.tare_values[selected_row - 1]

                # Bind the dropdown selection to update the tare values
                tare_var.trace("w", confirm_tare_selection)

                # Set the default tare to the first row
                self.tare = self.tare_values[0]
            else:
                messagebox.showinfo("Info", "No 'Tare' cells found above the 'x-axis' cell.")
                self.tare_values = None
                self.tare = None
            self.timestamps = df.iloc[x_axis_row + 1:, 0].values  # First column is timestamp
            self.distances = pd.to_numeric(
                df.iloc[x_axis_row, 3:].values,
                errors='coerce'
            )  # Row 33, columns from D onwards
            self.original_data = df.iloc[
                x_axis_row + 1:,
                3:
            ].apply(pd.to_numeric, errors='coerce').values  # Deformation values start from column D
            self.data = self.original_data.copy()  # Copy original data for manipulation
            self.current_timestamp_idx = 0

            # Update slider range
            self.slider.config(from_=0, to=len(self.data) - 1)
            self.slider.set(0)

            # Update stats after loading the file
            self.update_stats()

            self.plot_deformation()

            # Display the first 30 rows of the file in the data frame
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    lines = file.readlines()[:30]
                    self.data_text.config(state=tk.NORMAL)  # Enable editing temporarily
                    self.data_text.delete(1.0, tk.END)
                    self.data_text.insert(tk.END, "".join(lines))
                    self.data_text.config(state=tk.DISABLED)  # Make it read-only
            except (OSError, IOError) as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")
    def plot_deformation(self):
        """Plots the deformation values against distances for the current timestamp."""	
        if self.data is None:
            return

        self.ax.clear()

        # Plot locked lines
        for line_data in self.locked_lines:
            self.ax.plot(
                line_data['distances'],
                line_data['deformation_values'],
                label=f"Locked: {line_data['timestamp']}")
        # Plot the current line
        deformation_values = self.data[self.current_timestamp_idx]
        valid_indices = (~pd.isna(deformation_values)) & (~pd.isna(self.distances)) & \
                        (~np.isinf(deformation_values)) & (~np.isinf(self.distances))
        deformation_values = deformation_values[valid_indices]
        distances = self.distances[valid_indices]

        # Store the current line's data for hover tooltips
        self.current_plot_data = list(zip(distances, deformation_values))

        # Print deformation values to the console
        print(
            f"Deformation values for timestamp {self.timestamps[self.current_timestamp_idx]}: {deformation_values}"
        )
        self.ax.plot(distances, deformation_values, label=f"Current: {self.timestamps[self.current_timestamp_idx]}")
        self.ax.set_title(
            f"Deformation vs Distance\nTimestamp: {self.timestamps[self.current_timestamp_idx]}"
        )
        self.ax.set_xlabel("Distance")
        self.ax.set_ylabel("Deformation")
        self.ax.grid(True)

        # Limit the plot area to the range of the plotted values
        if len(distances) > 0 and len(deformation_values) > 0:
            self.ax.set_xlim([distances.min(), distances.max()])
            self.ax.set_ylim([deformation_values.min(), deformation_values.max()])

        # Set 10 equally spaced ticks for x-axis and y-axis
        self.ax.set_xticks(self.ax.get_xticks()[::max(1, len(self.ax.get_xticks()) // 10)])
        self.ax.set_yticks(self.ax.get_yticks()[::max(1, len(self.ax.get_yticks()) // 10)])

        self.ax.legend()  # Add legend to distinguish lines
        self.canvas.draw()

    def shift_timestamp(self, delta):
        """Shifts the current timestamp index by a given delta and updates the plot."""	
        if self.data is None:
            return

        new_idx = self.current_timestamp_idx + delta
        if 0 <= new_idx < len(self.data):
            self.current_timestamp_idx = new_idx
            self.plot_deformation()

    def update_timestamp(self, value):
        """Updates the current timestamp index based on the slider value and refreshes the plot."""
        if self.data is None:
            return

        self.current_timestamp_idx = int(value)
        self.slider_label.config(
            text=f"Timestamp Index: {self.current_timestamp_idx}"
        )
        self.update_stats()
        self.plot_deformation()

    def update_stats(self):
        """Updates the statistics labels with peak, average deformation, and current timestamp."""
        if self.data is None:
            return

        deformation_values = self.data[self.current_timestamp_idx]
        valid_values = deformation_values[~np.isnan(deformation_values) & ~np.isinf(deformation_values)]
        peak = valid_values.max() if len(valid_values) > 0 else "N/A"
        avg = valid_values.mean() if len(valid_values) > 0 else "N/A"
        timestamp = self.timestamps[self.current_timestamp_idx] if self.timestamps is not None else "N/A"
        self.peak_label.config(
            text=f"Peak Deformation: {peak}"
        )
        self.avg_label.config(
            text=f"Average Deformation: {avg}"
        )
        self.timestamp_label.config(
            text=f"Timestamp: {timestamp}"
        )
        self.position_label.config(
            text=f"Slider Position: {self.current_timestamp_idx}"
        )

    def toggle_zeroing(self):
        """Toggle zeroing mode to apply or remove tare values from the data."""
        if self.data is None or self.tare is None:
            return

        self.zeroing_enabled = not self.zeroing_enabled

        if self.zeroing_enabled:
            # Apply tare values individually for each x-axis distance
            self.data = self.original_data + self.tare
        else:
            # Restore the original data
            self.data = self.original_data.copy()

        self.plot_deformation()

    def zero_from_timestamp(self):
        """Zero the data based on the current timestamp by subtracting the values at that timestamp."""
        if self.data is None:
            return

        # Zero the data based on the current timestamp using the current state of self.data
        zeroing_values = self.data[self.current_timestamp_idx]  # Deformation values at the selected timestamp
        self.data = self.data - zeroing_values  # Subtract the selected timestamp's values from all data

        self.plot_deformation()

    def lock_line(self):
        """Locks the current line of deformation values and distances for later reference."""
        if self.data is None:
            return

        # Lock the current line
        deformation_values = self.data[self.current_timestamp_idx]
        valid_indices = (~pd.isna(deformation_values)) & (~pd.isna(self.distances)) & \
                        (~np.isinf(deformation_values)) & (~np.isinf(self.distances))
        deformation_values = deformation_values[valid_indices]
        distances = self.distances[valid_indices]

        if len(distances) > 0 and len(deformation_values) > 0:
            self.locked_lines.append({
                'distances': distances,
                'deformation_values': deformation_values,
                'timestamp': self.timestamps[self.current_timestamp_idx]
            })
            self.plot_deformation()

    def reset_graph(self):
        """Resets the graph to its original state, clearing locked lines and zeroing."""
        # Clear locked lines
        self.locked_lines = []

        # Reset zeroing
        self.zeroing_enabled = False
        self.data = self.original_data.copy()

        # Replot only the current line
        self.plot_deformation()

    def on_hover(self, event):
        """Handles mouse hover events to show tooltips for the closest point on the plot."""	
        if event.inaxes != self.ax or not hasattr(self, "current_plot_data"):
            return

        # Clear previous annotations
        for annotation in self.ax.texts:
            annotation.remove()

        # Find the closest point to the cursor
        closest_point = None
        min_distance = float("inf")
        for distance, deformation in self.current_plot_data:
            if event.xdata is None or event.ydata is None:
                continue
            cursor_distance = np.sqrt((event.xdata - distance) ** 2 + (event.ydata - deformation) ** 2)
            if cursor_distance < min_distance:
                min_distance = cursor_distance
                closest_point = (distance, deformation)

        if closest_point and min_distance < 0.1:  # Adjust sensitivity as needed
            tooltip_text = f"({closest_point[0]:.2f}, {closest_point[1]:.2f})"
            self.ax.annotate(
                tooltip_text,
                xy=closest_point,
                xytext=(10, 10),
                textcoords="offset points",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(arrowstyle="->")
            )
            self.canvas.draw_idle()

    def toggle_playback(self):
        """Toggles playback mode to run through timestamps automatically."""
        if self.playback_running:
            self.playback_running = False
            self.play_pause_button.config(text="⏵")
        else:
            self.playback_running = True
            self.play_pause_button.config(text="⏸")
            self.run_playback()

    def fast_forward(self):
        """Increases the playback speed for fast-forwarding through timestamps."""
        if self.playback_speed > 0:
            self.playback_speed = min(self.playback_speed * 2, self.max_playback_speed)
        else:
            self.playback_speed = 1  # Reset to normal forward speed

    def reverse(self):
        """Reverses the playback speed for going backward through timestamps."""
        if self.playback_speed < 0:
            self.playback_speed = max(self.playback_speed * 2, -self.max_playback_speed)
        else:
            self.playback_speed = -1  # Reset to normal reverse speed

    def run_playback(self):
        """Runs the playback by updating the timestamp index and refreshing the plot."""
        if not self.playback_running or self.data is None:
            return

        new_idx = self.current_timestamp_idx + self.playback_speed
        if 0 <= new_idx < len(self.data):
            self.current_timestamp_idx = new_idx
            self.slider.set(self.current_timestamp_idx)
            self.update_stats()
            self.plot_deformation()

        # Schedule the next playback step
        self.master.after(
            200 // abs(self.playback_speed),
            self.run_playback
        )

    def add_range(self):
        """Adds a new range selection"""	
        if self.data is None or self.distances is None:
            messagebox.showerror("Error", "No data loaded to add a range.")
            return

        # Create a new window for range selection
        range_window = tk.Toplevel(self.master)
        range_window.title("Select Range")

        # Center the range selection window
        self.center_window(range_window)

        tk.Label(
            range_window,
            text="Enter start and end of the range (in meters):"
        ).pack(pady=5)

        start_var = tk.DoubleVar()
        end_var = tk.DoubleVar()

        tk.Label(range_window, text="Start:").pack()
        start_entry = tk.Entry(range_window, textvariable=start_var)
        start_entry.pack()

        tk.Label(range_window, text="End:").pack()
        end_entry = tk.Entry(range_window, textvariable=end_var)
        end_entry.pack()

        def confirm_range():
            try:
                start = start_var.get()
                end = end_var.get()

                if start >= end:
                    raise ValueError("Start must be less than end.")

                # Validate range
                valid_indices = (self.distances >= start) & (self.distances <= end)
                if not valid_indices.any():
                    raise ValueError("No data points found in the specified range.")

                # Create a new plot window
                self.create_plot_window(start, end, valid_indices)
                range_window.destroy()
            except ValueError as e:
                messagebox.showerror(
                    "Error",
                    f"Invalid range: {e}"
                )
        confirm_button = tk.Button(
            range_window,
            text="Confirm",
            command=confirm_range
        )
        confirm_button.pack(pady=10)

    def create_plot_window(self, start, end, valid_indices):
        """Creates a new plot window for the specified range of distances and deformation values."""
        # Create a new window for the plot
        plot_window = tk.Toplevel(self.master)
        plot_window.title(
            f"Plot for Range {start:.2f}m to {end:.2f}m"
        )

        # Center the new window relative to the original window
        self.center_window(plot_window)

        # Create a figure and canvas for the new plot
        figure = plt.Figure(figsize=(8, 6))
        ax = figure.add_subplot(111)
        canvas = FigureCanvasTkAgg(figure, master=plot_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add Matplotlib's navigation toolbar for zoom and pan
        toolbar_frame = tk.Frame(plot_window)
        toolbar_frame.pack(fill=tk.X, pady=5)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()

        # Add a slider for the new plot
        slider_frame = tk.Frame(plot_window)
        slider_frame.pack(fill=tk.X, pady=5)

        slider = tk.Scale(
            slider_frame,
            from_=0,
            to=len(self.data) - 1,
            orient=tk.HORIZONTAL,
            length=700
        )
        slider.pack(side=tk.LEFT, padx=5)

        slider_label = tk.Label(
            slider_frame,
            text="Timestamp Index: 0"
        )
        slider_label.pack(side=tk.LEFT, padx=5)

        # Add control buttons
        control_frame = tk.Frame(plot_window)
        control_frame.pack(fill=tk.X, pady=5)

        locked_lines = []  # Maintain a separate list of locked lines for this window

        def update_plot(value):
            timestamp_idx = int(value)
            deformation_values = self.data[timestamp_idx][valid_indices]
            distances = self.distances[valid_indices]

            ax.clear()

            # Plot all locked lines
            for line_data in locked_lines:
                ax.plot(line_data['distances'], line_data['deformation_values'],
                        label=f"Locked: {line_data['timestamp']}")

            # Plot the current line
            ax.plot(
                distances,
                deformation_values,
                label=f"Timestamp: {self.timestamps[timestamp_idx]}"
            )
            ax.set_title(
                f"Deformation vs Distance\nRange: {start:.2f}m to {end:.2f}m"
            )
            ax.set_xlabel("Distance (m)")
            ax.set_ylabel("Deformation (microstrain)")
            ax.grid(True)
            ax.legend()
            canvas.draw()

            slider_label.config(text=f"Timestamp Index: {timestamp_idx}")

        def toggle_zeroing():
            """Toggle zeroing mode to apply or remove tare values from the data."""
            if self.zeroing_enabled:
                self.data = self.original_data.copy()
            else:
                if self.tare is not None:
                    # Apply tare values individually for the selected range
                    self.data = self.original_data + self.tare
            self.zeroing_enabled = not self.zeroing_enabled
            update_plot(slider.get())

        def zero_from_timestamp():
            """Zero the data based on the current timestamp by subtracting the values at that timestamp."""
            timestamp_idx = slider.get()
            zeroing_values = self.data[timestamp_idx]
            self.data = self.original_data - zeroing_values
            update_plot(slider.get())

        def lock_line():
            """Locks the current line of deformation values and distances for later reference."""
            timestamp_idx = slider.get()
            deformation_values = self.data[timestamp_idx][valid_indices]
            distances = self.distances[valid_indices]

            if len(distances) > 0 and len(deformation_values) > 0:
                locked_lines.append({
                    'distances': distances,
                    'deformation_values': deformation_values,
                    'timestamp': self.timestamps[timestamp_idx]
                })

            # Update the plot to include the locked lines
            update_plot(slider.get())

        def reset_graph():
            """Resets the graph to its original state, clearing locked lines and zeroing."""
            self.data = self.original_data.copy()
            update_plot(slider.get())

        def toggle_playback():
            """Toggles playback mode to run through timestamps automatically."""
            nonlocal playback_running
            playback_running = not playback_running
            if playback_running:
                run_playback()

        def fast_forward():
            """Increases the playback speed for fast-forwarding through timestamps."""
            nonlocal playback_speed
            playback_speed = min(playback_speed * 2, self.max_playback_speed)

        def reverse():
            """Reverses the playback speed for going backward through timestamps."""
            nonlocal playback_speed
            playback_speed = max(playback_speed * 2, -self.max_playback_speed)

        def run_playback():
            """Runs the playback by updating the timestamp index and refreshing the plot."""
            if not playback_running:
                return
            new_idx = slider.get() + playback_speed
            if 0 <= new_idx < len(self.data):
                slider.set(new_idx)
                update_plot(new_idx)

        def save_image():
            """Saves the current plot as an image file."""
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"),
                           ("All files", "*.*")])
            if file_path:
                figure.savefig(file_path)
                messagebox.showinfo("Info", f"Plot saved to {file_path}")

        def export_to_excel():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                loading_window, progress = self.show_loading_window(
                    "Exporting to Excel..."
                )
                try:
                    progress.set(10)
                    self.master.update_idletasks()

                    # Extract and transpose the selected range
                    selected_data = self.data[:, valid_indices].T
                    selected_distances = self.distances[valid_indices]
                    selected_timestamps = self.timestamps

                    # Create a DataFrame
                    df = pd.DataFrame(
                        selected_data,
                        columns=selected_timestamps
                    )
                    df.insert(0, "Distance", selected_distances)

                    progress.set(50)
                    self.master.update_idletasks()

                    # Save to Excel
                    df.to_excel(file_path, index=False)

                    progress.set(100)
                    self.master.update_idletasks()
                    messagebox.showinfo("Info", f"Data exported to {file_path}")
                except (OSError, ValueError) as e:
                    messagebox.showerror("Error", f"Failed to export data: {e}")
                finally:
                    loading_window.destroy()

        playback_running = False
        playback_speed = 1

        tk.Button(control_frame, text="Toggle Zeroing", command=toggle_zeroing).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Zero from Timestamp", command=zero_from_timestamp).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Lock Line", command=lock_line).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Reset Graph", command=reset_graph).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="⏯", command=toggle_playback).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="⏩", command=fast_forward).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="⏪", command=reverse).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save Image", command=save_image).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Export to Excel", command=export_to_excel).pack(side=tk.LEFT, padx=5)

        slider.config(command=update_plot)
        update_plot(0)  # Initialize the plot with the first timestamp

    def center_window(self, window):
        """Centers a given window relative to the main application window."""
        self.master.update_idletasks()
        x = self.master.winfo_x()
        y = self.master.winfo_y()
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        window_width = window.winfo_reqwidth()
        window_height = window.winfo_reqheight()

        new_x = x + (width // 2) - (window_width // 2)
        new_y = y + (height // 2) - (window_height // 2)

        window.geometry(
            f"+{new_x}+{new_y}"
        )

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
        self.plot_point(csv_file_path)
    def plot_point(self, csv_file_path):
        """Plots points from a CSV file against deformation values for the current timestamp."""
        try:
            # Load the CSV file starting from row 2
            points_df = pd.read_csv(csv_file_path, skiprows=1)
            required_columns = [
                "Point Number",
                "X Coordinate",
                "Y Coordinate"
            ]
            if not all(col in points_df.columns for col in required_columns):
                missing_columns = [
                    col for col in required_columns if col not in points_df.columns
                ]
                actual_columns = ", ".join(points_df.columns)
                messagebox.showerror(
                    "Error",
                    "CSV file must contain the following columns: "
                    f"{', '.join(required_columns)}.\n"
                    f"Missing columns: {', '.join(missing_columns)}.\n"
                    f"Actual columns in the file: {actual_columns}."
                )
                return

            deformation_values = self.data[self.current_timestamp_idx]
            valid_indices = (~pd.isna(deformation_values)) & (~pd.isna(self.distances)) & \
                            (~np.isinf(deformation_values)) & (~np.isinf(self.distances))
            deformation_values = deformation_values[valid_indices]

            # Ensure the number of deformation values matches the number of points
            if len(deformation_values) < len(points_df):
                deformation_values = np.append(
                    deformation_values,
                    [0] * (len(points_df) - len(deformation_values))
                )

            # Sort points and deformation values by deformation values to plot higher values last
            sorted_data = sorted(
                zip(
                    deformation_values,
                    points_df["X Coordinate"],
                    points_df["Y Coordinate"]
                ),
                key=lambda x: x[0]
            )
            deformation_values, x_coords, y_coords = zip(*sorted_data)

            # Check if the plot window already exists
            if not hasattr(self, "plot_window") or not self.plot_window.winfo_exists():
                # Create a new window for the plot
                self.plot_window = tk.Toplevel(self.master)
                self.plot_window.title(
                    f"Point Plot at Timestamp Index {self.current_timestamp_idx}"
                )

                # Center the new window relative to the original window
                self.center_window(self.plot_window)

                # Create a figure and canvas for the plot
                self.figure, self.ax = plt.subplots(
                    figsize=(10, 6)
                )
                self.canvas = FigureCanvasTkAgg(
                    self.figure,
                    master=self.plot_window
                )
                self.canvas.get_tk_widget().pack(
                    fill=tk.BOTH,
                    expand=True
                )

                # Add Matplotlib's navigation toolbar for zoom and pan
                toolbar_frame = tk.Frame(self.plot_window)
                toolbar_frame.pack(fill=tk.X, pady=5)
                toolbar = NavigationToolbar2Tk(
                    self.canvas,
                    toolbar_frame
                )
                toolbar.update()

                # Add buttons for adjusting the timestamp index
                control_frame = tk.Frame(self.plot_window)
                control_frame.pack(fill=tk.X, pady=5)

                tk.Button(
                    control_frame,
                    text="Previous",
                    command=lambda: self.update_timestamp_plot(
                        csv_file_path, -1
                    )
                ).pack(side=tk.LEFT, padx=5)
                tk.Button(
                    control_frame,
                    text="Next",
                    command=lambda: self.update_timestamp_plot(
                        csv_file_path, 1
                    )
                ).pack(side=tk.LEFT, padx=5)

            # Clear the previous plot
            self.ax.clear()

            # Plot the points with colors corresponding to deformation values
            # Create the scatter plot
            scatter = self.ax.scatter(
                x_coords,
                y_coords,
                c=deformation_values,
                cmap="viridis",
                s=50
            )

            self.ax.set_title(
                f"Point Plot at Timestamp Index {self.current_timestamp_idx}"
            )
            self.ax.set_xlabel("X Coordinate")
            self.ax.set_ylabel("Y Coordinate")
            self.ax.set_aspect('equal')  # Lock the aspect ratio to 1:1

            # Remove any existing colorbars before adding a new one
            if hasattr(self, "colorbar") and self.colorbar:
                self.colorbar.remove()
            self.colorbar = self.figure.colorbar(
                scatter,
                ax=self.ax,
                label="Deformation Value"
            )

            self.canvas.draw()

        except ValueError as e:
            messagebox.showerror(
                "Error",
                f"Failed to plot points: {e}"
            )

    def update_timestamp_plot(self, csv_file_path, step):
        """Updates the plot with the next or previous timestamp index"""
        try:
            new_index = self.current_timestamp_idx + step
            if 0 <= new_index < len(self.data):
                self.current_timestamp_idx = new_index
                if hasattr(self, "ax"):
                    self.ax.clear()  # Clear the previous plot
                self.plot_point(csv_file_path)  # Re-plot with the updated index
        except pd.errors.ParserError as e:
            messagebox.showerror(
                "Error",
                f"Failed to parse CSV file: {e}"
            )
        except ValueError as e:
            messagebox.showerror(
                "Error",
                f"Failed to plot points: {e}"
            )
if __name__ == "__main__":
    master = tk.Tk()
    app = DeformationApp(master)
    master.mainloop()