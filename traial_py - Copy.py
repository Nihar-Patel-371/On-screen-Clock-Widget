import json
import os
import customtkinter
import tkinter as tk
from tkinter import font as tkFont
from tkinter import colorchooser
from time import strftime
import math
import time
from ctypes import windll, byref, sizeof, c_int
from BlurWindow.blurWindow import blur
from BlurWindow.blurWindow import GlobalBlur
import ttk
from ttkthemes import ThemedTk
import pywinstyles


SETTINGS_FILE = "settings.json"

class DigitalClock(customtkinter.CTkToplevel):
    def __init__(self, parent, main_menu, font_family="Times New Roman", font_size=32, font_alpha=1.0, bg_alpha=1.0):
        super().__init__(parent)
        self.parent = parent
        self.main_menu = main_menu
        self.font_family = font_family
        self.font_size = font_size
        self.font_alpha = font_alpha
        self.bg_alpha = bg_alpha
        self.bg_color = '#0E141B'
        self.fg_color = '#E0E6EB'
        self.x = 0
        self.y = 0
        self.create_window()
        
    def create_window(self):
        self.parent.iconify()
        self.overrideredirect(True)
        self.title("Digital Clock")
        self.attributes('-alpha', self.bg_alpha)
        self.attributes('-topmost', True)
        self.configure(bg='black')

        # Custom title bar
        title_bar = customtkinter.CTkFrame(self, fg_color='black', height=50)
        title_bar.pack(fill='x')
        # Change the title bar color
        # HWND = windll.user32.GetParent(self.winfo_id())
        # windll.dwmapi.DwmSetWindowAttribute(
        #     HWND,
        #     35,
        #     byref(c_int(0x000000FF)),
        #     sizeof(c_int))


        close_button = tk.Button(title_bar, text='✖', command=self.close_window, bg='black', fg='white', bd=0, padx=10, pady=5, highlightthickness=0)
        close_button.pack(side='right')        
        maximize_button = tk.Button(title_bar, text='❐', command=self.maximize_window, bg='black', fg='white', bd=0, padx=10, pady=5, highlightthickness=0)
        maximize_button.pack(side='right')

        title_bar.bind('<ButtonPress-1>', self.start_move)
        title_bar.bind('<ButtonRelease-1>', self.stop_move)
        title_bar.bind('<B1-Motion>', self.move_window)

        # # Custom title bar

        self.clock_label = tk.Label(self, font=(self.font_family, self.font_size), background=self.bg_color, foreground=self.fg_color)
        self.clock_label.pack(anchor='center', fill='both', expand=True)

        # Add the gripper for resizing the window
        ttk.Style().configure('success.TSizegrip', background =self.bg_color, foreground="white")
        grip=ttk.Sizegrip(self, style='success.TSizegrip')
        grip.place(relx=1.0, rely=1.0, anchor="se")
        grip.bind("<B1-Motion>", self.move_window)

        print(self.winfo_x(), self.winfo_x())
        self.update_time()

    def color(hex):
        hWnd = windll.user32.GetForegroundWindow()
        blur(hWnd,hexColor=hex)

    def update_time(self):
        time_string = strftime('%H:%M:%S')
        self.clock_label.config(text=time_string)
        self.clock_label.after(1000, self.update_time)

    def close_window(self):
        if self:
            self.destroy()
            self.main_menu.deiconify()

    def minimize_window(self):
        self.attributes('-topmost', False)
        self.iconify()

    def maximize_window(self):
        if self.state() == 'zoomed':
            self.state('normal')
        else:
            self.state('zoomed')

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = 0
        self.y = 0

    def move_window(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        new_x = self.winfo_x() + deltax
        new_y = self.winfo_y() + deltay
        self.geometry(f"+{new_x}+{new_y}")

class AnalogClock(customtkinter.CTkToplevel):
    def __init__(self, parent, main_menu, clock_face="Classic", dial_type="Roman", hand_type="Classic", clock_alpha_a=1.0, bg_alpha_a=0.8):
        super().__init__(parent)
        self.parent = parent
        self.main_menu = main_menu
        self.clock_face = clock_face
        self.dial_type = dial_type
        self.hand_type = hand_type
        self.clock_alpha_a = clock_alpha_a
        self.bg_alpha_a = bg_alpha_a
        self.bg_color = '#0E141B'
        self.fg_color = '#E0E6EB'
        self.x = 0
        self.y = 0
        self.window_size = 300
        self.overrideredirect(True)
        self.configure(bg='black')
        self.attributes('-alpha', self.bg_alpha_a)
        self.attributes('-topmost', True)
        self.parent.iconify()
        self.geometry(f"{self.window_size}x{self.window_size+30}")

        # Custom title bar
        title_bar = tk.Frame(self, bg='black', relief='raised', bd=0, highlightthickness=0)
        title_bar.pack(fill='x')

        close_button = tk.Button(title_bar, text='✖', command=self.close_window, bg='black', fg='white', bd=0, padx=10, pady=5, highlightthickness=0)
        close_button.pack(side='right')
        maximize_button = tk.Button(title_bar, text='❐', command=self.maximize_window, bg='black', fg='white', bd=0, padx=10, pady=5, highlightthickness=0)
        maximize_button.pack(side='right')

        title_bar.bind('<ButtonPress-1>', self.start_move)
        title_bar.bind('<ButtonRelease-1>', self.stop_move)
        title_bar.bind('<B1-Motion>', self.move_window)

        self.canvas = tk.Canvas(self, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Add the gripper for resizing the window
        ttk.Style().configure('success.TSizegrip', background =self.bg_color, foreground="white")
        grip=ttk.Sizegrip(self, style='success.TSizegrip')
        grip.place(relx=1.0, rely=1.0, anchor="se")
        grip.bind("<B1-Motion>", self.move_window)

        self.update_clock()

    def draw_hand(self, angle, length, width, color):
        r = min(self.canvas.winfo_height()/2, self.canvas.winfo_width()/2)*0.95
        c_x = self.canvas.winfo_width()/2
        c_y = self.canvas.winfo_height()/2
        scale = r/150
        print(self.canvas.winfo_width(), self.canvas.winfo_height())
        x1 = c_x + (length * scale) * math.sin(math.radians(angle))
        y1 = c_y - (length * scale) * math.cos(math.radians(angle))
        self.canvas.create_line(c_x, c_y, x1, y1, width=width*scale, fill=color)

    def draw_face(self):
        r = min(self.canvas.winfo_height()/2, self.canvas.winfo_width()/2)*0.95
        c_x = self.canvas.winfo_width()/2
        c_y = self.canvas.winfo_height()/2
        scale = r/150
        p=0.05
        for i in range(12):
            angle = i * 30
            x0 = c_x + r * math.sin(math.radians(angle))
            y0 = c_y - r * math.cos(math.radians(angle))
            x1 = c_x + r * math.sin(math.radians(angle)) * 0.9
            y1 = c_y - r * math.cos(math.radians(angle)) * 0.9
            self.canvas.create_line(x0, y0, x1, y1, fill='white', width=6*scale)
        self.canvas.create_oval(c_x-r, c_y-r, c_x+r, c_y+r, outline='white', width=8*scale, tags=("notch",))
        self.canvas.create_oval(c_x-r*p, c_y-r*p, c_x+r*p, c_y+r*p, outline='white',  fill='#fff', tags=("notch",))

    def do_raise(self):
        self.canvas.tag_raise("notch")

    def update_clock(self):
        self.canvas.delete("all")
        self.draw_face()
        now = time.localtime()
        second = now.tm_sec
        minute = now.tm_min
        hour = now.tm_hour % 12

        self.draw_hand(second * 6, 110, 2, 'red')
        self.draw_hand(minute * 6 + second / 10, 90, 4, 'white')
        self.draw_hand(hour * 30 + minute / 2, 60, 6, 'white')
        self.after(1000, self.update_clock)

    def close_window(self):
        if self:
            self.destroy()
            self.main_menu.deiconify()

    def maximize_window(self):
        if self.state() == 'zoomed':
            self.state('normal')
        else:
            self.state('zoomed')

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = 0
        self.y = 0

    def move_window(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        new_x = self.winfo_x() + deltax
        new_y = self.winfo_y() + deltay
        self.geometry(f"+{new_x}+{new_y}")

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
    else:
        settings = {
            "clock_type": "Digital",
            "digital_clock": {
                "font_family": "Times New Roman",
                "font_size": 32,
                "font_alpha": 1.0,
                "bg_alpha": 0.8
            },
            "analog_clock": {
                "clock_face": "Classic",
                "dial_type": "Roman",
                "hand_type": "Classic",
                "clock_alpha_a": 1.0,
                "bg_alpha_a": 0.8
            }
        }

    # Ensure all keys are present
    if "clock_type" not in settings:
        settings["clock_type"] = "Digital"
    if "digital_clock" not in settings:
        settings["digital_clock"] = {
            "font_family": "Times New Roman",
            "font_size": 32,
            "font_alpha": 1.0,
            "bg_alpha": 0.8
        }
    else:
        if "font_family" not in settings["digital_clock"]:
            settings["digital_clock"]["font_family"] = "Times New Roman"
        if "font_size" not in settings["digital_clock"]:
            settings["digital_clock"]["font_size"] = 32
        if "font_alpha" not in settings["digital_clock"]:
            settings["digital_clock"]["font_alpha"] = 1.0
        if "bg_alpha" not in settings["digital_clock"]:
            settings["digital_clock"]["bg_alpha"] = 0.8

    if "analog_clock" not in settings:
        settings["analog_clock"] = {
            "clock_face": "Classic",
            "dial_type": "Roman",
            "hand_type": "Classic",
            "clock_alpha_a": 1.0,
            "bg_alpha_a": 0.8
        }
    else:
        if "clock_face" not in settings["analog_clock"]:
            settings["analog_clock"]["clock_face"] = "Classic"
        if "dial_type" not in settings["analog_clock"]:
            settings["analog_clock"]["dial_type"] = "Roman"
        if "hand_type" not in settings["analog_clock"]:
            settings["analog_clock"]["hand_type"] = "Classic"
        if "clock_alpha_a" not in settings["analog_clock"]:
            settings["analog_clock"]["clock_alpha_a"] = 1.0
        if "bg_alpha_a" not in settings["analog_clock"]:
            settings["analog_clock"]["bg_alpha_a"] = 0.8

    return settings

def main():
    settings = load_settings()
    current_clock_window = None
    
    main_window = customtkinter.CTk()
    windll.shcore.SetProcessDpiAwareness(1)
    main_window.title("Clock Widget Setup")
    window_width = 600
    window_height = 300
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()
    main_window.geometry(f"{str(window_width)}x{str(window_height)}+{int(screen_width/2)-int(window_width/2)}+{int(screen_height/2)-int(window_height/2)}")

    # Frame 1
    pane_1 = customtkinter.CTkFrame(main_window)
    pane_1.pack(fill='both', expand=True, side='left')
    # Digital Button and Analog Button
    clock_type = customtkinter.StringVar(value=settings["clock_type"])
    digital_radio = customtkinter.CTkRadioButton(pane_1, text="Digital Clock", variable=clock_type, value="Digital")
    digital_radio.pack(anchor='center', padx=20, pady=10)
    analog_radio = customtkinter.CTkRadioButton(pane_1, text="Analog Clock", variable=clock_type, value="Analog")
    analog_radio.pack(anchor='center', padx=20, pady=10)

    # Frame 2
    pane_2 = customtkinter.CTkFrame(main_window)
    pane_2.pack(fill='both', expand=True, anchor='center', side='left')
    # Additional options for Digital Clock
    fonts_family = list(tkFont.families())
    fonts_family.sort()
    alpha_val_font = customtkinter.DoubleVar(value=settings["digital_clock"]["font_alpha"])
    alpha_val_bg = customtkinter.DoubleVar(value=settings["digital_clock"]["bg_alpha"])

    font_label = customtkinter.CTkLabel(pane_2, text="Font Family:")
    font_family = customtkinter.StringVar(value=settings["digital_clock"]["font_family"])
    # font_dropdown = customtkinter.CTkOptionMenu(pane_2, variable=font_family, values=fonts_family)

    font_dropdown = ttk.Combobox(pane_2, textvariable=font_family, values=fonts_family)

    size_label = customtkinter.CTkLabel(pane_2, text="Font Size:")
    font_size = customtkinter.StringVar(value=str(settings["digital_clock"]["font_size"]))
    size_dropdown = ttk.Combobox(pane_2, textvariable=font_size, values=['16', '32', '48', '64', '72', '86', '96'])

    # alpha_font_label = customtkinter.CTkLabel(pane_2, text="Transparency of Font:")
    # alpha_font_scroll_bar = customtkinter.CTkSlider(pane_2, from_=0, to=1, variable=alpha_val_font)
    alpha_bg_label = customtkinter.CTkLabel(pane_2, text="Transparency of Background:")
    alpha_bg_scroll_bar = customtkinter.CTkSlider(pane_2, from_=0, to=1, variable=alpha_val_bg)

    # Additional options for Analog Clock
    clock_alpha_a = tk.DoubleVar(value=settings["analog_clock"]["clock_alpha_a"])
    bg_alpha_a = tk.DoubleVar(value=settings["analog_clock"]["bg_alpha_a"])

    face_label = customtkinter.CTkLabel(pane_2, text="Clock Face:")
    clock_face = customtkinter.StringVar(value=settings["analog_clock"]["clock_face"])
    face_dropdown = customtkinter.CTkOptionMenu(pane_2, variable=clock_face, values=["Classic"]) # , "Modern", "Minimal"
    dial_label = customtkinter.CTkLabel(pane_2, text="Dial Type:")
    dial_type = customtkinter.StringVar(value=settings["analog_clock"]["dial_type"])
    dial_dropdown = customtkinter.CTkOptionMenu(pane_2, variable=dial_type, values=["Roman"]) # , "Arabic", "Dot"
    hand_label = customtkinter.CTkLabel(pane_2, text="Hand Type:")
    hand_type = customtkinter.StringVar(value=settings["analog_clock"]["hand_type"])
    hand_dropdown = customtkinter.CTkOptionMenu(pane_2, variable=hand_type, values=["Classic"]) # , "Modern", "Minimal"
    alpha_clock_label = customtkinter.CTkLabel(pane_2, text="Transparency of Font:")
    alpha_clock_slider = customtkinter.CTkSlider(pane_2, from_=0, to=1, variable=clock_alpha_a)
    alpha_bg_label_a = customtkinter.CTkLabel(pane_2, text="Transparency of Background:")
    alpha_bg_slider = customtkinter.CTkSlider(pane_2, from_=0, to=1, variable=bg_alpha_a)

    def close_current_clock():
        nonlocal current_clock_window
        if current_clock_window:
            current_clock_window.close_window()
            current_clock_window = None

    def proceed():
        nonlocal current_clock_window
        close_current_clock()
        settings["clock_type"] = clock_type.get()
        if clock_type.get() == "Digital":
            settings["digital_clock"]["font_family"] = font_family.get()
            settings["digital_clock"]["font_size"] = int(font_size.get())
            settings["digital_clock"]["font_alpha"] = alpha_val_font.get()
            settings["digital_clock"]["bg_alpha"] = alpha_val_bg.get()
            current_clock_window = DigitalClock(main_window, main_window, font_family.get(), int(font_size.get()), alpha_val_font.get(), alpha_val_bg.get())
        elif clock_type.get() == "Analog":
            settings["analog_clock"]["clock_face"] = clock_face.get()
            settings["analog_clock"]["dial_type"] = dial_type.get()
            settings["analog_clock"]["hand_type"] = hand_type.get()
            settings["analog_clock"]["clock_alpha_a"] = clock_alpha_a.get()
            settings["analog_clock"]["bg_alpha_a"] = bg_alpha_a.get()
            current_clock_window = AnalogClock(main_window, main_window, clock_face.get(), dial_type.get(), hand_type.get(), clock_alpha_a.get(), bg_alpha_a.get())
        save_settings(settings)

    # Frame 3
    pane_3 = customtkinter.CTkFrame(main_window)
    pane_3.pack(fill='both', expand=True, anchor='center', side='left')

    # Proceed Button
    proceed_button = customtkinter.CTkButton(pane_3, text="Proceed", command=proceed)
    proceed_button.pack(pady=20)

    def on_select():
        if clock_type.get() == "Digital":
            font_label.pack(anchor='w', padx=20)
            font_dropdown.pack(anchor='w', padx=20)
            size_label.pack(anchor='w', padx=20, pady=10)
            size_dropdown.pack(anchor='w', padx=20)
            # alpha_font_label.pack(anchor='w', padx=20, pady=10)
            # alpha_font_scroll_bar.pack(anchor='w', padx=20)
            alpha_bg_label.pack(anchor='w', padx=20, pady=10)
            alpha_bg_scroll_bar.pack(anchor='w', padx=20)
            face_label.pack_forget()
            face_dropdown.pack_forget()
            dial_label.pack_forget()
            dial_dropdown.pack_forget()
            hand_label.pack_forget()
            hand_dropdown.pack_forget()
            alpha_clock_label.pack_forget()
            alpha_clock_slider.pack_forget()
            alpha_bg_label_a.pack_forget()
            alpha_bg_slider.pack_forget()
        else:
            font_label.pack_forget()
            font_dropdown.pack_forget()
            size_label.pack_forget()
            size_dropdown.pack_forget()
            # alpha_font_scroll_bar.pack_forget()
            # alpha_font_label.pack_forget()
            alpha_bg_scroll_bar.pack_forget()
            alpha_bg_label.pack_forget()
            face_label.pack(anchor='w', padx=20)
            face_dropdown.pack(anchor='w', padx=20)
            dial_label.pack(anchor='w', padx=20)
            dial_dropdown.pack(anchor='w', padx=20)
            hand_label.pack(anchor='w', padx=20)
            hand_dropdown.pack(anchor='w', padx=20)
            alpha_clock_label.pack(anchor='w', padx=20)
            alpha_clock_slider.pack(anchor='w', padx=20)
            alpha_bg_label_a.pack(anchor='w', padx=20)
            alpha_bg_slider.pack(anchor='w', padx=20)



    digital_radio.configure(command=on_select)
    analog_radio.configure(command=on_select)
    
    # Call on_select once to set initial state
    on_select()

    import ctypes

    myappid = 'clock.widget' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # main_window.iconbitmap('time_RkO_icon.ico')

    main_window.mainloop()

if __name__ == "__main__":
    main()