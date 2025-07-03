import plotter as plot

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
        plot.plot_deformation(self)

    # Schedule the next playback step
    self.master.after(
        200 // abs(self.playback_speed),
        self.run_playback
    )