import tkinter as tk
from tkinter import scrolledtext, messagebox
import time
from adb_utils import get_installed_apps, get_app_path, pull_apk, send_sms
from apk_utils import decode_apk, cleanup_apk_files
from manifest_parser import parse_manifest
from ai_analyzer import analyze_manifest_with_ai, analyze_dynamic_data_with_ai

class APKAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x600")
        self.root.title("APK Analyzer")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.show_initial_page()

    def show_initial_page(self):
        self.clear_frame()

        main_label = tk.Label(self.main_frame, text="APK Analyzer", font=("Arial", 18))
        main_label.pack(pady=30)

        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        # Create buttons with fixed width, placed in the button frame
        static_button = tk.Button(button_frame, text="Static Analysis", command=self.show_static_analysis, font=("Arial", 14), width=20)
        static_button.grid(row=0, column=0, padx=10)  # Place button using grid

        dynamic_button = tk.Button(button_frame, text="Dynamic Analysis", command=self.show_dynamic_analysis, font=("Arial", 14), width=20)
        dynamic_button.grid(row=0, column=1, padx=10)  # Place button side by side using grid

    def show_static_analysis(self):
        self.clear_frame()

        title_label = tk.Label(self.main_frame, text="Static Analysis - Android APK Analyzer", font=("Arial", 16))
        title_label.pack(pady=10)

        self.selected_app = tk.StringVar()

        self.scroll_text = scrolledtext.ScrolledText(self.main_frame, width=100, height=20, font=('Arial', 12), padx=10, pady=10)
        self.scroll_text.pack(padx=20, pady=20, ipadx=10, ipady=10)

        self.scroll_text.bind("<Button-1>", self.on_text_click)
        self.scroll_text.bind("<Motion>", self.on_text_hover)
        self.scroll_text.bind("<Leave>", self.on_text_leave)

        apps = get_installed_apps()
        for app in apps:
            self.scroll_text.insert(tk.END, f"{app}\n")

        input_frame = tk.Frame(self.main_frame)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Filter apps:", font=('Arial', 16)).pack(side=tk.LEFT, padx=10)
        self.entry = tk.Entry(input_frame)
        self.entry.pack(side=tk.LEFT, padx=10)
        self.entry.bind("<KeyRelease>", self.update_listbox)

        tk.Label(input_frame, text="Enter app details:", font=('Arial', 16)).pack(side=tk.LEFT, padx=5)
        self.app_info_entry = tk.Entry(input_frame)
        self.app_info_entry.pack(side=tk.LEFT)

        analyze_button = tk.Button(self.main_frame, text="Analyze", command=self.on_analyze, font=("Arial", 14), width=20)
        analyze_button.pack(pady=10)

        back_button = tk.Button(self.main_frame, text="Back", command=self.show_initial_page, font=("Arial", 14), width=10)
        back_button.pack(pady=10)

        self.result_text = scrolledtext.ScrolledText(self.main_frame, width=200, height=100, font=("Arial", 16), padx=10, pady=10)
        self.result_text.pack(padx=20, pady=20)

        self.result_text.configure(wrap=tk.WORD, relief=tk.GROOVE, borderwidth=2)
        self.result_text.tag_configure("center", justify="center")
        self.result_text.insert(tk.END, "Analysis Results:\n", "center")

    def show_dynamic_analysis(self):
        self.clear_frame()

        title_label = tk.Label(self.main_frame, text="Dynamic Analysis - Android APK Analyzer", font=("Arial", 16))
        title_label.pack(pady=40)

        input_frame = tk.Frame(self.main_frame)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Enter app details:", font=('Arial', 16)).pack(side=tk.LEFT, padx=5)
        self.app_info_entry_dyna = tk.Entry(input_frame)
        self.app_info_entry_dyna.pack(side=tk.LEFT)

        info_label = tk.Label(self.main_frame, text="Test the following data steal", font=("Arial", 14))
        info_label.pack(pady=10)

        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        # Create buttons with fixed width, placed in the button frame

        message_button = tk.Button(button_frame, text="Message", command=self.handle_message, font=("Arial", 14), width=20)
        message_button.grid(row=0, column=0, padx=10)

        audio_button = tk.Button(button_frame, text="Other Audio", command=self.handle_audio, font=("Arial", 14), width=20)
        audio_button.grid(row=0, column=1, padx=10)

        file_button = tk.Button(button_frame, text="File", command=self.handle_file, font=("Arial", 14), width=20)
        file_button.grid(row=0, column=2, padx=10)

        back_button = tk.Button(self.main_frame, text="Back", command=self.show_initial_page, font=("Arial", 14), width=10)
        back_button.pack(pady=10)

        self.result_text_dynamic = scrolledtext.ScrolledText(self.main_frame, width=200, height=100, font=("Arial", 16), padx=10, pady=10)
        self.result_text_dynamic.pack(padx=20, pady=20)

        self.result_text_dynamic.configure(wrap=tk.WORD, relief=tk.GROOVE, borderwidth=2)
        self.result_text_dynamic.tag_configure("center", justify="center")
        self.result_text_dynamic.insert(tk.END, "Analysis Results:\n", "center")

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def on_text_hover(self, event):
        self.scroll_text.config(cursor="hand2")

    def on_text_leave(self, event):
        self.scroll_text.config(cursor="xterm")

    def on_text_click(self, event):
        index = self.scroll_text.index(f"@{event.x},{event.y}")
        line_number = index.split('.')[0]
        line_text = self.scroll_text.get(f"{line_number}.0", f"{line_number}.end")
        self.selected_app.set(line_text.strip())
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.selected_app.get())
        print(f"Selected app: {self.selected_app.get()}")

    def update_listbox(self, event):
        typed_text = self.entry.get().lower()
        filtered_apps = [app for app in get_installed_apps() if typed_text in app.lower()]
        self.scroll_text.delete(1.0, tk.END)
        for app in filtered_apps:
            self.scroll_text.insert(tk.END, f"{app}\n")

    def on_analyze(self):
        if self.selected_app.get():
            selected_app = self.selected_app.get()
            apk_path = get_app_path(selected_app)
            if apk_path:
                apk_filename = pull_apk(apk_path, selected_app)
                if apk_filename:
                    decode_apk(apk_filename)
                    manifest_data = parse_manifest(apk_filename)
                    appinfo = self.app_info_entry.get()
                    if manifest_data:
                        analysis = analyze_manifest_with_ai(manifest_data, appinfo)
                        self.result_text.delete(1.0, tk.END)
                        self.result_text.insert(tk.END, analysis)
                        cleanup_apk_files(apk_filename)
        else:
            messagebox.showerror("Error", "No app selected!")

    def handle_message(self):
        with open("requests.log", "w") as logfile:
            logfile.write("")
        message = "When will you reach home honey"
        phone_number = "+9449334323"
        
        send_sms(phone_number, message)
        time.sleep(2)
        appinfo_dyna = self.app_info_entry_dyna.get()
        analysis = analyze_dynamic_data_with_ai(appinfo_dyna)
        self.result_text_dynamic.delete(1.0, tk.END)
        self.result_text_dynamic.insert(tk.END, analysis)

    def handle_audio(self):
        print("Other Audio button clicked")

    def handle_file(self):
        print("File button clicked")

def run_gui():
    root = tk.Tk()
    app = APKAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()