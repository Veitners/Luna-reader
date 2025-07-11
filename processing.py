import pandas as pd
import numpy as np
from tkinter import messagebox
import plotter as plot

def find_x_axis_row(df):
    """Find the row index of the cell containing 'x-axis'."""
    df = df.astype(str)
    x_axis_cell = df.apply(lambda row: row.str.contains('x-axis', case=False, na=False)).stack()
    if not x_axis_cell.empty:
        x_axis_row, _ = x_axis_cell.idxmax()
        return x_axis_row
    else:
        return None

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

    plot.plot_deformation(self)

def zero_from_timestamp(self):
    """Zero the data based on the current timestamp by subtracting the values at that timestamp."""
    if self.data is None:
        return

    # Zero the data based on the current timestamp using the current state of self.data
    zeroing_values = self.data[self.current_timestamp_idx]  # Deformation values at the selected timestamp
    self.data = self.data - zeroing_values  # Subtract the selected timestamp's values from all data
    plot.plot_deformation(self)

def update_timestamp(self, value):
    """Updates the current timestamp index based on the slider value and refreshes the plot."""
    if self.data is None:
        return

    self.current_timestamp_idx = int(value)
    self.slider_label.config(
        text=f"Timestamp Index: {self.current_timestamp_idx}"
    )
    self.update_stats()
    plot.plot_deformation(self)

def update_timestamp_plot(self, csv_file_path, step):
    """Updates the plot with the next or previous timestamp index"""
    try:
        new_index = self.current_timestamp_idx + step
        if 0 <= new_index < len(self.data):
            self.current_timestamp_idx = new_index
            if hasattr(self, "ax"):
                self.ax.clear()  # Clear the previous plot
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

def shift_timestamp(self, delta):
    """Shifts the current timestamp index by a given delta and updates the plot."""	
    if self.data is None:
        return

    new_idx = self.current_timestamp_idx + delta
    if 0 <= new_idx < len(self.data):
        self.current_timestamp_idx = new_idx
        plot.plot_deformation(self)