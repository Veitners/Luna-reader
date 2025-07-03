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
    self.canvas.draw()


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
                command=lambda: self.update_timestamp_plot(step=-1)
            ).pack(side=tk.LEFT, padx=5)
            tk.Button(
                control_frame,
                text="Next",
                command=lambda: self.update_timestamp_plot(step=1)
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