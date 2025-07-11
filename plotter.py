import tkinter as tk
from tkinter import messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def plot_deformation(self):
    """Plots the deformation values against distances for the current timestamp."""
    if self.data is None:
        return

    self.ax.clear()

    # Plot locked lines
    for line_data in self.locked_lines:
        self.ax.plot(
            line_data["distances"],
            line_data["deformation_values"],
            label=line_data["label"],
            linestyle="--",
            color=line_data["color"]
        )

    deformation_values = self.data[self.current_timestamp_idx]
    valid_indices = (~pd.isna(deformation_values)) & (~pd.isna(self.distances)) & \
                    (self.distances >= self.range_start) & (self.distances <= self.range_end)

    deformation_values = deformation_values[valid_indices]
    distances = self.distances[valid_indices]

    # Store the current line's data for hover tooltips
    self.current_plot_data = list(zip(distances, deformation_values))

    # Print deformation values to the console
    print(
        f"Plotting deformation values: {deformation_values} against distances: {distances}"
    )
    self.ax.plot(distances, deformation_values, label=f"Current: {self.timestamps[self.current_timestamp_idx]}")
    self.ax.set_title(
        f"Deformation Plot for Timestamp: {self.timestamps[self.current_timestamp_idx]}"
    )
    self.ax.set_xlabel("Distance")
    self.ax.set_ylabel("Deformation")
    self.ax.grid(True)

    # Limit the plot area to the range of the plotted values
    if len(distances) > 0 and len(deformation_values) > 0:
        self.ax.set_xlim([distances.min(), distances.max()])
        # --- Use y-axis min/max from UI if set ---
        try:
            ymin = float(self.ymin_var.get())
        except ValueError:
            ymin = deformation_values.min()
        try:
            ymax = float(self.ymax_var.get())
        except ValueError:
            ymax = deformation_values.max()
        self.ax.set_ylim([ymin, ymax])

    # Set 10 equally spaced ticks for x-axis and y-axis
    self.ax.set_xticks(self.ax.get_xticks()[::max(1, len(self.ax.get_xticks()) // 10)])
    self.ax.set_yticks(self.ax.get_yticks()[::max(1, len(self.ax.get_yticks()) // 10)])

    self.ax.legend()  # Add legend to distinguish lines
    try:
        self.canvas.draw()
    except tk.TclError as e:
        messagebox.showerror(
            "Canvas Update Error",
            f"Failed to update the canvas due to a Tkinter error: {str(e)}. This might occur if the window is closed or the canvas is not properly initialized."
        )
def lock_line(self):
    """Locks the current line of deformation values and distances for later reference."""
    if self.data is None:
        return

    deformation_values = self.data[self.current_timestamp_idx]
    valid_indices = (~pd.isna(deformation_values)) & (~pd.isna(self.distances)) & \
                    (~np.isinf(deformation_values)) & (~np.isinf(self.distances))

    deformation_values = deformation_values[valid_indices]
    distances = self.distances[valid_indices]

    colors = ['red', 'blue', 'green', 'orange', 'purple']
    line_style = '-'

    if len(distances) > 0 and len(deformation_values) > 0:
        color_index = len(self.locked_lines) % len(colors)
        self.locked_lines.append({
            "distances": distances,
            "deformation_values": deformation_values,
            "label": f"Locked: {self.timestamps[self.current_timestamp_idx]}",
            "color": colors[color_index],
            "line_style": line_style
        })
        self.plot_deformation(self)
def reset_graph(self):
    """Resets the graph to its original state, clearing locked lines and zeroing."""
    self.locked_lines.clear()
    self.zeroing_enabled = False
    self.data = self.original_data.copy()
    self.plot_deformation(self)
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
def reset_yaxis_limits(self):
    """Reset y-axis min/max entry fields and replot."""
    self.ymin_var.set("")
    self.ymax_var.set("")
    self.plot_deformation(self)
def plot_spatial_layout(self):
    """Plots the spatial layout of points with deformation values as colors."""
    if self.data is None or self.distances is None:
        messagebox.showerror("Error", "No deformation data or coordinates loaded.")
        return

    try:
        # Load the real-world coordinates from the CSV file
        points_df = pd.read_csv(self.csv_file_path, skiprows=1)
        x_coords = points_df["X Coordinate"].values
        y_coords = points_df["Y Coordinate"].values

        num_points = len(x_coords)
        num_deformations = self.data.shape[1]

        if num_deformations > num_points:
            # Truncate deformation data to match number of points
            self.data = self.data[:, :num_points]
        elif num_points > num_deformations:
            # Pad deformation data with zeros to match number of points
            pad_width = num_points - num_deformations
            self.data = np.pad(self.data, ((0, 0), (0, pad_width)), mode='constant', constant_values=0)

        # Create a new window for the plot
        if not hasattr(self, "plot_window") or self.plot_window is None or not self.plot_window.winfo_exists():
            self.plot_window = tk.Toplevel(self.master)
            self.plot_window.title("Spatial Layout of Deformation")
            self.center_window(self.plot_window)

            self.figure = plt.Figure(figsize=(10, 6))
            self.ax = self.figure.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_window)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            toolbar_frame = tk.Frame(self.plot_window)
            toolbar_frame.pack(fill=tk.X, pady=5)
            toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
            toolbar.update()

        # Plot the initial scatterplot
        deformation_values = self.data[self.current_timestamp_idx]
        sorted_indices = np.argsort(deformation_values)
        x_coords = x_coords[sorted_indices]
        y_coords = y_coords[sorted_indices]
        deformation_values = deformation_values[sorted_indices]

        # Increase point size for better visibility
        scatter = self.ax.scatter(
            x_coords, y_coords, c=deformation_values, cmap="viridis", s=50
        )
        self.colorbar = self.figure.colorbar(scatter, ax=self.ax)
        self.ax.set_title(f"Deformation at Timestamp: {self.timestamps[self.current_timestamp_idx]}")
        self.ax.set_xlabel("X Coordinate")
        self.ax.set_ylabel("Y Coordinate")

        # Update the plot dynamically with the slider
        def update_plot(timestamp_idx):
            timestamp_idx = int(timestamp_idx)
            self.current_timestamp_idx = timestamp_idx
            deformation_values = self.data[timestamp_idx]

            # Adjust deformation values and coordinates for mismatches
            num_points = len(x_coords)
            num_deformations = len(deformation_values)

            if num_points > num_deformations:
                deformation_values = np.pad(deformation_values, (0, num_points - num_deformations), constant_values=0)
            elif num_deformations > num_points:
                deformation_values = deformation_values[:num_points]

            scatter.set_array(deformation_values)
            self.ax.set_title(f"Deformation at Timestamp: {self.timestamps[timestamp_idx]}")
            self.canvas.draw()

        slider_frame = tk.Frame(self.plot_window)
        slider_frame.pack(fill=tk.X, pady=5)
        slider = tk.Scale(
            slider_frame, from_=0, to=len(self.timestamps) - 1, orient=tk.HORIZONTAL,
            command=update_plot, length=500
        )
        slider.pack()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while plotting: {e}")