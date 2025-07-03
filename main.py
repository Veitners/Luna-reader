"""
Author: Edgars Veitners
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import loader as load
import processing as util
import plotter as plot
import window
import player
import autoupdate
import os

repo_url = "https://github.com/Veitners/Luna-reader"
current_version = "0.0.1"  # Replace with your current version

def check_for_updates():
    """Checks for updates and prompts the user."""
    autoupdate.check_for_update(repo_url, current_version)

class DeformationApp:
    """Main application class for viewing"""
    def __init__(self, root):
        self.master = root
        self.master.title("Deformation over Distance Viewer")

        # Configure grid layout for resizing
        app_root = self.master
        # Configure grid rows and columns using a loop for brevity
        for i, w in enumerate([0, 0, 0, 0, 0, 1, 0, 0]):
            app_root.rowconfigure(i, weight=w)
        app_root.columnconfigure(0, weight=1)

        # Frame to hold the load button and file label
        self.load_frame = tk.Frame(app_root)
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
            self.load_frame, text="Open .tsv File",
            command=lambda: load.load_file(self)
        )
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Button to load the CSV file
        self.load_csv_button = tk.Button(
            self.load_frame, text="Load XY CSV",
            command=load.load_csv_file
        )
        self.load_csv_button.pack(side=tk.LEFT, padx=5)
        # Label to display the loaded file name
        self.file_label = tk.Label(
            self.load_frame, text="No file loaded", fg="gray"
        )
        self.file_label.pack(side=tk.LEFT, padx=5)

        # Frame to group zeroing-related buttons
        self.zeroing_frame = tk.LabelFrame(
            app_root, text="Zeroing Options", padx=10, pady=10
        )
        self.zeroing_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.zeroing_frame.columnconfigure(0, weight=1)

        # Button to toggle zeroing
        self.zeroing_button = tk.Button(
            self.zeroing_frame, text="Toggle Zeroing",
            command=lambda: util.toggle_zeroing(self)
        )
        self.zeroing_button.pack(side=tk.LEFT, padx=5)

        # Button to zero data from the selected timestamp
        self.zero_from_timestamp_button = tk.Button(
            self.zeroing_frame, text="Zero from Timestamp",
            command=lambda: util.zero_from_timestamp(self)
        )
        self.zero_from_timestamp_button.pack(side=tk.LEFT, padx=5)

        # Button to add a new range
        self.add_range_button = tk.Button(
            self.zeroing_frame, text="Add Range",
            command=self.add_range
        )
        self.add_range_button.pack(side=tk.LEFT, padx=5)

        # Zeroing state
        self.zeroing_enabled = False

        # Frame to hold playback controls (moved above the slider)
        self.playback_frame = tk.Frame(app_root)
        self.playback_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.playback_frame.columnconfigure(0, weight=1)

        # Frame to hold the lock, reset, and playback buttons
        self.button_frame = tk.Frame(app_root)
        self.button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        # Button to reset the graph
        self.reset_button = tk.Button(
            self.button_frame, text="Reset Graph",
            command=lambda: plot.reset_graph(self)
        )
        self.reset_button.pack(side=tk.RIGHT, padx=5)

        # Button to lock the current line
        self.lock_button = tk.Button(
            self.button_frame, text="Lock Line",
            command=lambda: plot.lock_line(self)
        )
        self.lock_button.pack(side=tk.RIGHT, padx=5)

        # Play/Pause toggle button
        self.play_pause_button = tk.Button(
            self.button_frame, text="⏯",
            command=lambda: player.toggle_playback(self)
        )
        self.play_pause_button.pack(side=tk.LEFT, padx=5)

        # Fast Forward button
        self.fast_forward_button = tk.Button(
            self.button_frame, text="⏩",
            command=lambda: player.fast_forward(self)
        )
        self.fast_forward_button.pack(side=tk.LEFT, padx=5)

        # Reverse button
        self.reverse_button = tk.Button(
            self.button_frame, text="⏪",
            command=lambda: player.reverse(self)
        )
        self.reverse_button.pack(side=tk.LEFT, padx=5)

        # Frame to hold the slider and its label
        self.slider_frame = tk.Frame(app_root)
        self.slider_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        self.slider_frame.columnconfigure(0, weight=1)
        # Slider for navigation
        self.slider = tk.Scale(
            self.slider_frame, from_=0, to=0, orient=tk.HORIZONTAL,
            command=lambda value: util.update_timestamp(self, value),
            length=700
        )
        self.slider.pack(side=tk.LEFT, padx=5)

        # Label to display the current timestamp index
        self.slider_label = tk.Label(
            self.slider_frame, text="Timestamp Index: 0"
        )
        self.slider_label.pack(side=tk.LEFT, padx=5)

        # List to store locked lines
        self.locked_lines = []

        # Frame to display the first rows of the .tsv file (spanning from top to bottom)
        self.data_frame = tk.Frame(app_root)
        self.data_frame.grid(row=0, column=1, rowspan=6, sticky="ns", padx=10, pady=5)
        self.data_frame.columnconfigure(0, weight=1)

        # Add a scrollbar for the data display
        self.data_scrollbar = tk.Scrollbar(self.data_frame, orient=tk.VERTICAL)
        self.data_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Text widget to display the data (read-only)
        self.data_text = tk.Text(
            self.data_frame, wrap=tk.NONE, yscrollcommand=self.data_scrollbar.set,
            width=40, state=tk.DISABLED
        )
        self.data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.data_scrollbar.config(command=self.data_text.yview)

        # Placeholder for the figure (adjusted to column 0)
        self.figure = plt.Figure(figsize=(8, 6))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=app_root)
        self.canvas.get_tk_widget().grid(
            row=5, column=0, sticky="nsew", padx=10, pady=5
        )

        # Frame to hold the toolbar
        self.toolbar_frame = tk.Frame(app_root)
        self.toolbar_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=5)
        self.toolbar_frame.columnconfigure(0, weight=1)

        # Add Matplotlib's navigation toolbar for zoom and pan
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

        # Configure resizing for the canvas
        app_root.rowconfigure(5, weight=1)
        app_root.columnconfigure(0, weight=1)

        # Frame to display deformation statistics
        self.stats_frame = tk.Frame(app_root)
        self.stats_frame.grid(row=7, column=0, sticky="ew", padx=10, pady=5)
        self.stats_frame.columnconfigure(0, weight=1)

        # Labels for statistics
        self.peak_label = tk.Label(self.stats_frame, text="Peak Deformation: N/A")
        self.peak_label.pack(side=tk.LEFT, padx=5)

        self.avg_label = tk.Label(self.stats_frame, text="Average Deformation: N/A")
        self.avg_label.pack(side=tk.LEFT, padx=5)

        self.timestamp_label = tk.Label(self.stats_frame, text="Timestamp: N/A")
        self.timestamp_label.pack(side=tk.LEFT, padx=5)

        self.position_label = tk.Label(self.stats_frame, text="Slider Position: 0")
        self.position_label.pack(side=tk.LEFT, padx=5)

        # Playback state
        self.playback_speed = 1  # 1 for normal, >1 for fast forward, <0 for reverse
        self.playback_running = False

        # Maximum playback speed
        self.max_playback_speed = 8

        # Data holders
        self.data = None
        self.timestamps = []
        self.distances = None
        self.current_timestamp_idx = 0
        self.original_data = None  # Initialize original_data to avoid pylint error

        # Enable interactive mode for tooltips
        # self.figure.canvas.mpl_connect("motion_notify_event", plot.on_hover)

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

        # Initialize range_start and range_end attributes
        self.range_start = None
        self.range_end = None

        # Set default values for range_start and range_end
        self.range_start = float('-inf')
        self.range_end = float('inf')

        # --- Add y-axis min/max controls ---
        self.yaxis_frame = tk.Frame(app_root)
        self.yaxis_frame.grid(row=8, column=0, sticky="ew", padx=10, pady=5)
        self.yaxis_frame.columnconfigure(0, weight=1)

        tk.Label(self.yaxis_frame, text="Y min:").pack(side=tk.LEFT, padx=2)
        self.ymin_var = tk.StringVar()
        self.ymin_entry = tk.Entry(
            self.yaxis_frame, textvariable=self.ymin_var, width=8
        )
        self.ymin_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(self.yaxis_frame, text="Y max:").pack(side=tk.LEFT, padx=2)
        self.ymax_var = tk.StringVar()
        self.ymax_entry = tk.Entry(
            self.yaxis_frame, textvariable=self.ymax_var, width=8
        )
        self.ymax_entry.pack(side=tk.LEFT, padx=2)
        # Update button commands to pass `self` explicitly
        self.set_yaxis_button = tk.Button(
            self.yaxis_frame, text="Apply Y Limits",
            command=lambda: plot.plot_deformation(self)
        )
        self.set_yaxis_button.pack(side=tk.LEFT, padx=5)
        self.reset_yaxis_button = tk.Button(
            self.yaxis_frame, text="Reset Y Limits",
            command=lambda: plot.reset_yaxis_limits(self)
        )
        self.reset_yaxis_button.pack(side=tk.LEFT, padx=5)

        # Add a button to check for updates
        self.update_button = tk.Button(
            self.load_frame, text="Check for Updates",
            command=check_for_updates
        )
        self.update_button.pack(side=tk.LEFT, padx=5)

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
            loading_window, orient="horizontal", length=250,
            mode="determinate", variable=progress_var
        )
        progress_bar.pack(pady=10)

        return loading_window, progress_var

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
            range_window, text="Enter start and end of the range (in meters):"
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
                window.create_plot_window(self, start, end, valid_indices)
                range_window.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid range: {e}")
        confirm_button = tk.Button(
            range_window, text="Confirm", command=confirm_range
        )
        confirm_button.pack(pady=10)

    def center_window(self, dialog_window):
        """Centers a given window relative to the main application window."""
        self.master.update_idletasks()
        x = self.master.winfo_x()
        y = self.master.winfo_y()
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        window_width = dialog_window.winfo_reqwidth()
        window_height = dialog_window.winfo_reqheight()

        new_x = x + (width // 2) - (window_width // 2)
        new_y = y + (height // 2) - (window_height // 2)

        dialog_window.geometry(f"+{new_x}+{new_y}")

    def update_stats(self):
        """Updates the statistics displayed in the stats_frame."""
        if (
            self.data is None or not hasattr(self.data, '__len__') or len(self.data) == 0 or
            self.current_timestamp_idx >= (len(self.data) if hasattr(self.data, '__len__') else 0)
        ):
            self.peak_label.config(text="Peak Deformation: N/A")
            self.avg_label.config(text="Average Deformation: N/A")
            self.timestamp_label.config(text="Timestamp: N/A")
            self.position_label.config(text="Slider Position: 0")
        else:
            # Ensure self.data is a numpy array for subscripting
            if not isinstance(self.data, (np.ndarray, list)):
                self.data = np.array(self.data)
            current_data = self.data[self.current_timestamp_idx]
            valid_data = current_data[~np.isnan(current_data)]
            if len(valid_data) > 0:
                peak_deformation = np.max(valid_data)
                avg_deformation = np.mean(valid_data)
                self.peak_label.config(
                    text=f"Peak Deformation: {peak_deformation:.2f}"
                )
                self.avg_label.config(
                    text=f"Average Deformation: {avg_deformation:.2f}"
                )
            else:
                self.peak_label.config(text="Peak Deformation: N/A")
                self.avg_label.config(text="Average Deformation: N/A")
            self.timestamp_label.config(
                text=f"Timestamp: {self.timestamps[self.current_timestamp_idx]}"
            )
            self.position_label.config(
                text=f"Slider Position: {self.current_timestamp_idx}"
            )

    def run_playback(self):
        """Delegates playback functionality to player.py."""
        try:
            player.run_playback(self)
        except AttributeError as e:
            messagebox.showerror(
                "Playback Error",
                f"An error occurred during playback: {e}"
            )


if __name__ == "__main__":
    master = tk.Tk()
    app = DeformationApp(master)
    master.mainloop()
