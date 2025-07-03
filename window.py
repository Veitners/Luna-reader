import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def create_plot_window(self, start, end, valid_indices):
    """Creates a new plot window for the specified range of distances and deformation values."""
    # Create a new window for the plot
    plot_window = tk.Toplevel(self.master)
    plot_window.title(f"Plot for Range {start:.2f}m to {end:.2f}m")

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
        """Updates the plot based on the slider value and applies persistent Y-axis limits."""
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

        # Apply persistent Y-axis limits
        ymin = float(ymin_var.get()) if ymin_var.get() else None
        ymax = float(ymax_var.get()) if ymax_var.get() else None
        ax.set_ylim(ymin, ymax)

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
        locked_lines.clear()  # Clear all locked lines
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
        playback_speed = max(playback_speed // 2, -self.max_playback_speed)

        # Ensure playback speed is negative for reverse
        if playback_speed > 0:
            playback_speed = -1

    def run_playback():
        """Runs the playback by updating the timestamp index and refreshing the plot."""
        if not playback_running:
            return
        new_idx = slider.get() + playback_speed
        if 0 <= new_idx < len(self.data):
            slider.set(new_idx)
            update_plot(new_idx)
        # Schedule the next playback step
        plot_window.after(100, run_playback)

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

    # Move Y-axis controls to a new row below the control frame and align them to the left side of the window
    yaxis_frame = tk.Frame(plot_window)
    yaxis_frame.pack(side=tk.LEFT, anchor="w", pady=5)

    tk.Label(yaxis_frame, text="Y min:").pack(side=tk.LEFT, padx=2)
    ymin_var = tk.StringVar()
    ymin_entry = tk.Entry(yaxis_frame, textvariable=ymin_var, width=8)
    ymin_entry.pack(side=tk.LEFT, padx=2)

    tk.Label(yaxis_frame, text="Y max:").pack(side=tk.LEFT, padx=2)
    ymax_var = tk.StringVar()
    ymax_entry = tk.Entry(yaxis_frame, textvariable=ymax_var, width=8)
    ymax_entry.pack(side=tk.LEFT, padx=2)

    def apply_yaxis_limits():
        """Applies the Y-axis limits entered by the user and updates the graph."""
        try:
            ymin = float(ymin_var.get()) if ymin_var.get() else None
            ymax = float(ymax_var.get()) if ymax_var.get() else None

            if ymin is not None and ymax is not None and ymin >= ymax:
                raise ValueError("Y min must be less than Y max.")

            ax.set_ylim(ymin, ymax)
            canvas.draw()  # Trigger a redraw of the graph
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid Y-axis limits: {e}")

    def reset_yaxis_limits():
        """Reset y-axis min/max entry fields and replot."""
        ymin_var.set("")
        ymax_var.set("")
        ax.set_ylim(None, None)  # Reset limits to default
        canvas.draw()

    tk.Button(yaxis_frame, text="Apply Y Limits", command=apply_yaxis_limits).pack(side=tk.LEFT, padx=5)
    tk.Button(yaxis_frame, text="Reset Y Limits", command=reset_yaxis_limits).pack(side=tk.LEFT, padx=5)

    slider.config(command=update_plot)
    update_plot(0)  # Initialize the plot with the first timestamp

    # Initialize the plot for the new window
    update_plot(0)