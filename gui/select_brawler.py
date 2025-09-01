import json
import tkinter as tk
from math import ceil

import customtkinter as ctk
import pyautogui
from PIL import Image
from customtkinter import CTkImage
from utils import load_toml_as_dict
from gui.hub import initialize_themes_file

debug = load_toml_as_dict("cfg/general_config.toml")['super_debug'] == "yes"
orig_screen_width, orig_screen_height = 1920, 1080
width, height = pyautogui.size()
width_ratio = width / orig_screen_width
height_ratio = height / orig_screen_height
scale_factor = min(width_ratio, height_ratio)
pyla_version = load_toml_as_dict("./cfg/general_config.toml")['pyla_version']
initialize_themes_file("cfg/themes.toml")
all_themes = load_toml_as_dict("cfg/themes.toml")
last_theme = all_themes.get("last_theme", "community")
themes = all_themes.get(last_theme, all_themes["community"])

class SelectBrawler:

    def __init__(self, data_setter, brawlers):
        self.app = ctk.CTk()

        square_size = int(75 * scale_factor)
        amount_of_rows = ceil(len(brawlers)/10) + 1
        necessary_height = (int(145 * scale_factor) + amount_of_rows*square_size + (amount_of_rows-1)*int(3 * scale_factor))
        self.app.title(f"PylaAI v{pyla_version}")
        self.brawlers = brawlers

        self.app.geometry(f"{str(int(860 * scale_factor))}x{necessary_height}+{str(int(600 * scale_factor))}")
        self.data_setter = data_setter

        self.app.configure(fg_color=themes["background_color"])



        self.images = []
        self.brawlers_data = []
        self.farm_type = ""

        for brawler in self.brawlers:
            img_path = f"./api/assets/brawler_icons/{brawler}.png"
            img = Image.open(img_path)

            img_tk = CTkImage(img, size=(square_size, square_size))
            self.images.append((brawler, img_tk))  # Store tuple of brawler name and image

        # Entry widget for filtering
        self.filter_var = tk.StringVar()
        self.filter_entry = ctk.CTkEntry(
            self.app, textvariable=self.filter_var,
            placeholder_text="Type brawler name...", font=("", int(20 * scale_factor)), width=int(200 * scale_factor),
            fg_color=themes["secondary_color"], border_color=themes["border_color"], text_color=themes["text_color"]
        )
        ctk.CTkLabel(self.app, text="Write brawler", font=("Comic sans MS", int(20 * scale_factor)),
                     text_color=themes["primary_color"]).place(x=int(scale_factor * 373), y=int(scale_factor * 20))
        self.filter_entry.place(x=int(340 * scale_factor), y=int(scale_factor * 52))
        self.filter_var.trace_add("write", lambda *args: self.update_images(self.filter_var.get()))

        # Frame to hold the images
        self.image_frame = ctk.CTkFrame(self.app, fg_color=themes["background_color"])
        self.image_frame.place(x=0, y=int(100 * scale_factor))

        self.update_images("")
        ctk.CTkButton(self.app, text="Start", command=self.start_bot, fg_color=themes["primary_color"],
                      text_color=themes["text_color"],
                      font=("Comic sans MS", int(25 * scale_factor)), border_color=themes["border_color"],
                      border_width=int(2 * scale_factor)).place(x=int(390 * scale_factor), y=int((necessary_height-60) * scale_factor))

        ctk.CTkButton(self.app, text="Load Brawler Config", command=self.load_brawler_config, fg_color=themes["primary_color"],
                      text_color=themes["text_color"],
                      font=("Comic sans MS", int(25 * scale_factor)), border_color=themes["border_color"],
                      border_width=int(2 * scale_factor)).place(x=int(10 * scale_factor),
                                                                y=int((necessary_height-60) * scale_factor))
        self.app.mainloop()

    def set_farm_type(self, value):
        self.farm_type = value

    def start_bot(self):
        self.data_setter(self.brawlers_data)
        self.app.destroy()

    def load_brawler_config(self):
        # open file select dialog to select a json file
        file_path = filedialog.askopenfilename(
            title="Select Brawler Config File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    brawlers_data = json.load(file)
                    try:
                        brawlers_data[0]['push_until']
                        for brawler_data in brawlers_data:
                            # if we find a brawler that has already reached it's goal, we remove it from the list
                            push_type = brawler_data["type"]
                            if brawler_data["push_until"] <= brawler_data[push_type]:
                                brawlers_data.remove(brawler_data)
                        self.brawlers_data = brawlers_data
                        print("Brawler data loaded successfully.")
                    except Exception as e:
                        print("Invalid data format. Expected a list of brawler data.", e)
            except Exception as e:
                print(f"Error loading brawler data: {e}")

    def on_image_click(self, brawler):
        self.open_brawler_entry(brawler)

    def open_brawler_entry(self, brawler):
        top = ctk.CTkToplevel(self.app)
        top.configure(fg_color=themes["background_color"])
        top.geometry(
            f"{str(int(300 * scale_factor))}x{str(int(450 * scale_factor))}+{str(int(1100 * scale_factor))}+{str(int(200 * scale_factor))}")
        top.title("Enter Brawler Data")
        top.attributes("-topmost", True)

        push_until_var = tk.StringVar()
        push_until_entry = ctk.CTkEntry(
            top, textvariable=push_until_var, fg_color=themes["secondary_color"], text_color=themes["text_color"],
            border_color=themes["border_color"], border_width=int(2 * scale_factor), height=int(28 * scale_factor)
        )

        trophies_var = tk.StringVar()
        trophies_entry = ctk.CTkEntry(
            top, textvariable=trophies_var, fg_color=themes["secondary_color"], text_color=themes["text_color"],
            border_color=themes["border_color"], border_width=int(2 * scale_factor), height=int(28 * scale_factor)
        )

        mastery_var = tk.StringVar()
        mastery_entry = ctk.CTkEntry(
            top, textvariable=mastery_var, fg_color=themes["secondary_color"], text_color=themes["text_color"],
            border_color=themes["border_color"], border_width=int(2 * scale_factor), height=int(28 * scale_factor)
        )

        current_win_streak_var = tk.StringVar(value="0")  # Set the default value to "0"
        current_win_streak_entry = ctk.CTkEntry(
            top, textvariable=current_win_streak_var, fg_color=themes["secondary_color"], text_color=themes["text_color"],
            border_color=themes["border_color"], border_width=int(2 * scale_factor), height=int(28 * scale_factor)
        )

        auto_pick_var = tk.BooleanVar(value=True)  # Checkbox variable, ticked by default
        auto_pick_checkbox = ctk.CTkCheckBox(
            top, text="Auto-pick Brawler in game", variable=auto_pick_var,
            fg_color=themes["primary_color"], text_color=themes["text_color"], checkbox_height=int(24 * scale_factor)
        )

        def submit_data():
            push_until_value = push_until_var.get()
            push_until_value = int(push_until_value) if push_until_value.isdigit() else ""
            trophies_value = int(trophies_var.get())
            mastery_value = mastery_var.get()
            mastery_value = int(mastery_value) if mastery_value.isdigit() else ""
            current_win_streak_value = current_win_streak_var.get()
            if self.farm_type == "trophies" and mastery_value == "":
                mastery_value = 0
            data = {
                "brawler": brawler,
                "push_until": push_until_value,
                "trophies": trophies_value,
                "mastery": mastery_value,
                "type": self.farm_type,
                "automatically_pick": auto_pick_var.get(),
                "win_streak": int(current_win_streak_value)
            }

            if data["type"] == "":
                if data["trophies"] <= data["mastery"]:
                    data["type"] = "trophies"
                else:
                    data["type"] = "mastery"

            self.brawlers_data = [item for item in self.brawlers_data if item["brawler"] != data["brawler"]]
            self.brawlers_data.append(data)

            if debug: print("Selected Brawler Data :", self.brawlers_data)
            top.destroy()

        submit_button = ctk.CTkButton(
            top, text="Submit", command=submit_data, fg_color=themes["primary_color"],
            border_color=themes["border_color"],
            text_color=themes["text_color"], border_width=int(2 * scale_factor), width=int(80 * scale_factor)
        )

        farm_type_button_frame = ctk.CTkFrame(top, width=int(200 * scale_factor), height=int(50 * scale_factor),
                                              fg_color=themes["background_color"])

        self.mastery_button = ctk.CTkButton(farm_type_button_frame, text="Mastery", width=int(85 * scale_factor),
                                            command=lambda: self.set_farm_type_color("mastery"),
                                            hover_color=themes["accent_color"],
                                            font=("", int(15 * scale_factor)),
                                            fg_color=themes["secondary_color"],
                                            border_color=themes["border_color"],
                                            text_color=themes["text_color"],
                                            border_width=int(2 * scale_factor)
                                            )
        self.trophies_button = ctk.CTkButton(farm_type_button_frame, text="Trophies", width=int(85 * scale_factor),
                                             command=lambda: self.set_farm_type_color("trophies"),
                                             hover_color=themes["accent_color"],
                                             font=("", int(15 * scale_factor)),
                                             fg_color=themes["secondary_color"],
                                             border_color=themes["border_color"],
                                             text_color=themes["text_color"],
                                             border_width=int(2 * scale_factor)
                                             )

        self.trophies_button.place(x=int(10 * scale_factor))
        self.mastery_button.place(x=int(110 * scale_factor))

        ctk.CTkLabel(top, text=f"Brawler: {brawler}", font=("Comic sans MS", int(20 * scale_factor)),
                     text_color=themes["primary_color"]).pack(
            pady=int(7 * scale_factor))
        farm_type_button_frame.pack()
        ctk.CTkLabel(top, text="Push Until", font=("Comic sans MS", int(15 * scale_factor)),
                     text_color=themes["text_color"]).pack()
        push_until_entry.pack(pady=int(4 * scale_factor))
        ctk.CTkLabel(top, text="Trophies", font=("Comic sans MS", int(15 * scale_factor)),
                     text_color=themes["text_color"]).pack()
        trophies_entry.pack(pady=int(4 * scale_factor))
        ctk.CTkLabel(top, text="Mastery", font=("Comic sans MS", int(15 * scale_factor)),
                     text_color=themes["text_color"]).pack()
        mastery_entry.pack(pady=int(4 * scale_factor))
        ctk.CTkLabel(top, text="Brawler's Win Streak", font=("Comic sans MS", int(15 * scale_factor)),
                     text_color=themes["text_color"]).pack()
        current_win_streak_entry.pack(pady=int(4 * scale_factor))
        auto_pick_checkbox.pack(pady=int(4 * scale_factor))  # Add the checkbox to the UI
        submit_button.pack(pady=int(7 * scale_factor))

    def set_farm_type_color(self, value):
        self.farm_type = value
        if value == "mastery":
            self.mastery_button.configure(fg_color=themes["primary_color"])
            self.trophies_button.configure(fg_color=themes["secondary_color"])
        else:
            self.mastery_button.configure(fg_color=themes["secondary_color"])
            self.trophies_button.configure(fg_color=themes["primary_color"])

    def update_images(self, filter_text):
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        row_num = 0
        col_num = 0

        for brawler, img_tk in self.images:
            if brawler.startswith(filter_text.lower()):
                label = ctk.CTkLabel(self.image_frame, image=img_tk, text="")
                label.bind("<Button-1>", lambda e, b=brawler: self.on_image_click(b))  # Bind click event
                label.grid(row=row_num, column=col_num, padx=int(5 * scale_factor), pady=int(3 * scale_factor))

                col_num += 1
                if col_num == 10:  # Move to the next row after 10 columns
                    col_num = 0
                    row_num += 1


def dummy_data_setter(data):
    print("Data set:", data)
