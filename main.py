import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyautogui
import threading
import time
from datetime import timedelta
import json
import os
import sys
import pystray
from PIL import Image, ImageDraw
import keyboard
import psutil
import win32gui
import win32con
from pathlib import Path
import math
import random

class MouseJigglerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Jiggler")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Initialize variables
        self.is_running = False
        self.is_paused = False
        self.current_pattern = "horizontal"
        self.theme_mode = "light"
        self.settings = self.load_settings()
        
        # Configure the root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configure style
        self.configure_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Create menu
        self.create_menu()
        
        # Create and pack widgets
        self.create_widgets()
        
        # Add watermark
        self.create_watermark()
        
        # Initialize system tray
        self.setup_system_tray()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        self.jiggler_thread = None
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Settings", command=self.save_settings)
        file_menu.add_command(label="Load Settings", command=self.load_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Movement Pattern", command=self.show_pattern_settings)
        settings_menu.add_command(label="Startup Settings", command=self.show_startup_settings)
        settings_menu.add_command(label="Theme Settings", command=self.toggle_theme)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_widgets(self):
        # Title section
        self.create_title_section()
        
        # Control section
        self.create_control_section()
        
        # Status section
        self.create_status_section()
        
        # Output section
        self.create_output_section()
        
    def create_title_section(self):
        title_frame = ttk.Frame(self.main_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, 
                              text="Mouse Jiggler",
                              style="Title.TLabel")
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(title_frame,
                                 text="Keep your system active with advanced features",
                                 style="Subtitle.TLabel")
        subtitle_label.grid(row=1, column=0, pady=(0, 10))
        
    def create_control_section(self):
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        control_frame.grid_columnconfigure(3, weight=1)
        
        # Time inputs
        time_frame = ttk.Frame(control_frame)
        time_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=(0, 20))
        
        ttk.Label(time_frame, text="Hours:").grid(row=0, column=0, padx=(0, 5))
        self.hours_var = tk.StringVar()
        ttk.Entry(time_frame, textvariable=self.hours_var, width=5).grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(time_frame, text="Minutes:").grid(row=0, column=2, padx=(0, 5))
        self.minutes_var = tk.StringVar()
        ttk.Entry(time_frame, textvariable=self.minutes_var, width=5).grid(row=0, column=3)
        
        # Movement pattern
        pattern_frame = ttk.Frame(control_frame)
        pattern_frame.grid(row=0, column=2, sticky="w", padx=(0, 20))
        
        ttk.Label(pattern_frame, text="Pattern:").grid(row=0, column=0, padx=(0, 5))
        self.pattern_var = tk.StringVar(value="horizontal")
        pattern_combo = ttk.Combobox(pattern_frame, textvariable=self.pattern_var, 
                                   values=["horizontal", "circular", "random"], 
                                   state="readonly", width=10)
        pattern_combo.grid(row=0, column=1)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=3, sticky="e")
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_jiggler,
                                     style="Action.TButton")
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pause", command=self.toggle_pause,
                                     state="disabled", style="Action.TButton")
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_jiggler,
                                    state="disabled", style="Action.TButton")
        self.stop_button.grid(row=0, column=2, padx=5)
        
    def create_status_section(self):
        status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Status indicators
        self.status_label = ttk.Label(status_frame, text="Ready", style="Status.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, style="Status.Horizontal.TProgressbar")
        self.progress_bar.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # CPU usage
        self.cpu_label = ttk.Label(status_frame, text="CPU: 0%", style="Status.TLabel")
        self.cpu_label.grid(row=0, column=2, sticky="e", padx=(10, 0))
        
    def create_output_section(self):
        output_frame = ttk.LabelFrame(self.main_frame, text="Activity Log", padding="10")
        output_frame.grid(row=3, column=0, sticky="nsew")
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame,
                                                   wrap=tk.WORD,
                                                   font=("Consolas", 10),
                                                   background="#ffffff",
                                                   padx=10,
                                                   pady=10)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        
    def create_watermark(self):
        watermark_frame = ttk.Frame(self.main_frame)
        watermark_frame.grid(row=4, column=0, sticky="se", pady=(5, 0))
        
        watermark_text = "Developed by Niyas"
        watermark_label = ttk.Label(
            watermark_frame,
            text=watermark_text,
            font=("Helvetica", 8),
            foreground="#808080"
        )
        watermark_label.grid(row=0, column=0)
        watermark_label.configure(style="Watermark.TLabel")
        
    def configure_styles(self):
        style = ttk.Style()
        
        # Configure colors
        self.colors = {
            "light": {
                "bg": "#f0f0f0",
                "fg": "#000000",
                "accent": "#007bff",
                "success": "#28a745",
                "warning": "#ffc107",
                "error": "#dc3545"
            },
            "dark": {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "accent": "#0d6efd",
                "success": "#198754",
                "warning": "#ffc107",
                "error": "#dc3545"
            }
        }
        
        # Configure styles for different widgets
        style.configure("Title.TLabel", 
                       font=("Helvetica", 24, "bold"),
                       padding=10)
        
        style.configure("Subtitle.TLabel",
                       font=("Helvetica", 12),
                       padding=5)
        
        style.configure("Status.TLabel",
                       font=("Helvetica", 10),
                       padding=5)
        
        style.configure("Action.TButton",
                       font=("Helvetica", 11, "bold"),
                       padding=10)
        
        style.configure("Watermark.TLabel",
                       background=self.colors["light"]["bg"],
                       foreground="#808080")
        
        # Configure progress bar
        style.configure("Status.Horizontal.TProgressbar",
                       troughcolor=self.colors["light"]["bg"],
                       background=self.colors["light"]["accent"])
        
    def setup_system_tray(self):
        # Create system tray icon
        image = Image.new('RGB', (64, 64), color='red')
        dc = ImageDraw.Draw(image)
        dc.rectangle([(0, 0), (63, 63)], fill='blue')
        
        menu = (
            pystray.MenuItem('Show', self.show_window),
            pystray.MenuItem('Start', self.start_jiggler),
            pystray.MenuItem('Stop', self.stop_jiggler),
            pystray.MenuItem('Exit', self.quit_app)
        )
        
        self.icon = pystray.Icon("mouse_jiggler", image, "Mouse Jiggler", menu)
        
    def bind_shortcuts(self):
        self.root.bind('<Control-s>', lambda e: self.start_jiggler())
        self.root.bind('<Control-p>', lambda e: self.toggle_pause())
        self.root.bind('<Control-x>', lambda e: self.stop_jiggler())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        
    def start_jiggler(self):
        if self.is_running:
            return
            
        try:
            hours = int(self.hours_var.get()) if self.hours_var.get() else 0
            minutes = int(self.minutes_var.get()) if self.minutes_var.get() else 0
            
            if hours == 0 and minutes == 0:
                messagebox.showwarning("Warning", "Please enter a duration.")
                return
                
            self.is_running = True
            self.is_paused = False
            
            # Update UI
            self.start_button.configure(state="disabled")
            self.pause_button.configure(state="normal")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text="Running")
            self.progress_var.set(0)
            
            self.output_text.delete(1.0, tk.END)
            self.log_message(f"Starting mouse jiggler for {hours} hours and {minutes} minutes...")
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
            self.monitor_thread.start()
            
            # Start jiggler thread
            self.jiggler_thread = threading.Thread(
                target=self.mouse_jiggler,
                args=(hours, minutes),
                daemon=True
            )
            self.jiggler_thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter numbers for hours and minutes.")
            
    def stop_jiggler(self):
        if not self.is_running:
            return
            
        self.is_running = False
        self.is_paused = False
        
        # Update UI
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Stopped")
        
        self.log_message("Mouse jiggler stopped.")
        
    def toggle_pause(self):
        if not self.is_running:
            return
            
        self.is_paused = not self.is_paused
        
        # Update UI
        self.pause_button.configure(text="Resume" if self.is_paused else "Pause")
        self.status_label.configure(text="Paused" if self.is_paused else "Running")
        
        self.log_message("Mouse jiggler " + ("paused" if self.is_paused else "resumed"))
        
    def mouse_jiggler(self, hours, minutes):
        total_seconds = hours * 3600 + minutes * 60
        end_time = time.time() + total_seconds
        direction = 1
        move_distance = 100
        initial_pos = pyautogui.position()
        
        while time.time() < end_time and self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue
                
            remaining = int(end_time - time.time())
            rem_time = str(timedelta(seconds=remaining))
            
            # Update progress
            progress = ((total_seconds - remaining) / total_seconds) * 100
            self.root.after(0, self.progress_var.set, progress)
            
            # Move mouse based on pattern
            if self.pattern_var.get() == "horizontal":
                x, y = pyautogui.position()
                new_x = x + move_distance * direction
                pyautogui.moveTo(new_x, y, duration=0.2)
                direction *= -1
            elif self.pattern_var.get() == "circular":
                x, y = pyautogui.position()
                radius = 50
                angle = time.time() * 2
                new_x = x + radius * math.cos(angle)
                new_y = y + radius * math.sin(angle)
                pyautogui.moveTo(new_x, new_y, duration=0.2)
            else:  # random
                x, y = pyautogui.position()
                new_x = x + random.randint(-move_distance, move_distance)
                new_y = y + random.randint(-move_distance, move_distance)
                pyautogui.moveTo(new_x, new_y, duration=0.2)
            
            log_entry = f"[{time.strftime('%H:%M:%S')}] Moved mouse | Time left: {rem_time}"
            self.root.after(0, self.log_message, log_entry)
            
            time.sleep(3)
            
        # Return mouse to original position
        pyautogui.moveTo(initial_pos)
        self.root.after(0, self.stop_jiggler)
        
    def monitor_system(self):
        while self.is_running:
            # Update CPU usage
            cpu_percent = psutil.cpu_percent()
            self.root.after(0, self.cpu_label.configure, 
                          {"text": f"CPU: {cpu_percent}%"})
            time.sleep(1)
            
    def log_message(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        
    def quit_app(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.stop_jiggler()
            self.icon.stop()
            self.root.quit()
            
    def show_shortcuts(self):
        shortcuts = """
Keyboard Shortcuts:
Ctrl+S: Start
Ctrl+P: Pause/Resume
Ctrl+X: Stop
Ctrl+Q: Quit
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
        
    def show_about(self):
        about = """
Mouse Jiggler Pro
Version 2.0

A professional tool to keep your system active
with advanced features and customization options.

Developed by Niyas
        """
        messagebox.showinfo("About", about)
        
    def toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.configure_styles()
        # Update all widgets with new theme
        self.update_theme()
        
    def update_theme(self):
        colors = self.colors[self.theme_mode]
        self.root.configure(bg=colors["bg"])
        self.main_frame.configure(style="Main.TFrame")
        self.output_text.configure(bg=colors["bg"], fg=colors["fg"])
        
    def save_settings(self):
        settings = {
            "pattern": self.pattern_var.get(),
            "theme": self.theme_mode,
            "geometry": self.root.geometry()
        }
        
        with open("settings.json", "w") as f:
            json.dump(settings, f)
            
        messagebox.showinfo("Settings", "Settings saved successfully!")
        
    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                return json.load(f)
        except:
            return {
                "pattern": "horizontal",
                "theme": "light",
                "geometry": "800x600"
            }
            
    def show_pattern_settings(self):
        # Create pattern settings window
        pattern_window = tk.Toplevel(self.root)
        pattern_window.title("Movement Pattern Settings")
        pattern_window.geometry("300x200")
        
        # Add pattern settings here
        
    def show_startup_settings(self):
        # Create startup settings window
        startup_window = tk.Toplevel(self.root)
        startup_window.title("Startup Settings")
        startup_window.geometry("300x200")
        
        # Add startup settings here

def main():
    root = tk.Tk()
    app = MouseJigglerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
