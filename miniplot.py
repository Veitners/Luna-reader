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
                   ("All files", "*.*")]
    )
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