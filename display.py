from typing import List
import tkinter as tk

from bus import EventBus, DV01Events


class DV01Ladder(tk.Frame):
    def __init__(self, parent, event_bus: EventBus, buckets: List[int]):
        super().__init__(parent)
        self.event_bus = event_bus
        self.buckets = buckets
        self.labels = {}
        self.previous_values = {}
        self._build_ui()
        self.event_bus.subscribe(DV01Events.DV01_UPDATED, self.update_data)
    
    def update_data(self, dv01_data: dict):
        for bucket, new_val in dv01_data.items():
            label = self.labels.get(bucket)
            if label:
                old_val = self.previous_values[bucket]
                if new_val != old_val:
                    self.previous_values[bucket] = new_val
                    label.configure(text=f"{new_val:,.2f}")
                    self._flash_label(label)

    def _build_ui(self):
        # Headers
        tk.Label(self, text="Bucket", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5, pady=3)
        tk.Label(self, text="DV01 (EUR)", font=("Arial", 11, "bold")).grid(row=0, column=1, padx=5, pady=3)

        # Rows
        for i, bucket in enumerate(self.buckets):
            tk.Label(self, text=f"{bucket}Y", font=("Arial", 10)).grid(row=i+1, column=0, sticky="w", padx=5)

            val_label = tk.Label(self, text="0.00", font=("Arial", 10), width=10)
            val_label.grid(row=i+1, column=1, padx=5)
            self.labels[bucket] = val_label
            self.previous_values[bucket] = 0.0

    def _flash_label(self, label, color="#ffff99"):
        original = label.cget("background")
        label.configure(background=color)
        self.after(250, lambda: label.configure(background=original))
