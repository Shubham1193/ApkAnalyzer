import subprocess
import xml.etree.ElementTree as ET
import google.generativeai as genai
import os
import shutil
import tkinter as tk
from tkinter import scrolledtext, messagebox
import time as t  

# Configure the API key for Google Generative AI
genai.configure(api_key="AIzaSyC5NMftqNr1LeLSxPRDvfinai4LN5YpplQ")

# Getting the list of apps 
def get_installed_apps():
    try:
        result = subprocess.run(['adb', 'shell', 'pm', 'list', 'packages'], capture_output=True, text=True, check=True)
        packages = [line.split(":")[1] for line in result.stdout.splitlines()]
        return packages
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to list installed packages: {e}")
        return []

# Getting the Exact path of the App in phone 
def get_app_path(package_name):
    try:
        result = subprocess.run(['adb', 'shell', 'pm', 'path', package_name], capture_output=True, text=True, check=True)
        apk_path = result.stdout.split(':')[1].strip()
        return apk_path
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to get the path for {package_name}: {e}")
        return None

# Pull the app from the phone to device
def pull_apk(apk_path, package_name):
    try:
        filename = f"{package_name.split('.')[-1]}.apk"
        subprocess.run(['adb', 'pull', apk_path, filename], check=True)
        print(f"APK for {package_name} pulled successfully: {filename}")
        return filename
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to pull the APK for {package_name}: {e}")
        return None

# Decode the app 
def decode_apk(apk_filename):
    try:
        subprocess.run(['java', '-jar', 'apktool.jar', 'd', apk_filename, '-o', f"{apk_filename}-decoded"], check=True)
        print(f"APK decoded successfully: {apk_filename}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to decode the APK: {e}")

# Parse the manifest
def parse_manifest(apk_path):
    try:
        tree = ET.parse(f'{apk_path}-decoded/AndroidManifest.xml')
        root = tree.getroot()

        permissions = [elem.attrib['{http://schemas.android.com/apk/res/android}name'] for elem in root.findall('uses-permission')]
        services = [elem.attrib['{http://schemas.android.com/apk/res/android}name'] for elem in root.findall('application/service')]
        receivers = [elem.attrib['{http://schemas.android.com/apk/res/android}name'] for elem in root.findall('application/receiver')]
        intents = [elem.attrib['{http://schemas.android.com/apk/res/android}name'] for elem in root.findall('.//intent-filter/action')]

        manifest_data = {
            "Permissions": permissions,
            "Services": services,
            "Broadcast Receivers": receivers,
            "Intents": intents
        }

        return manifest_data
    except Exception as e:
        print(f"An error occurred while parsing the manifest file: {e}")
        return {}

# Analyze the data
def analyze_manifest_with_ai(manifest_data, appinfo):
    model = genai.GenerativeModel('gemini-1.5-flash')
    safe = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]
    prompt = (
        "I'm analyzing the AndroidManifest data from an APK. This app is about "
        f"{appinfo}. Please help me identify any potentially suspicious permissions, services, or components that could indicate malicious behavior or potential security risks. "
        "For each item you find, please explain why it might be concerning. for the safety for user "

        "Here's the manifest data: "
        f"Permissions:\n{manifest_data.get('Permissions', [])}\n\n"
        f"Services:\n{manifest_data.get('Services', [])}\n\n"
        f"Broadcast Receivers:\n{manifest_data.get('Broadcast Receivers', [])}\n\n"
        f"Intents:\n{manifest_data.get('Intents', [])}\n"

        "Please provide your analysis in a concise and informative way.In simple 100 word paragraph withour any special character"
    )
    try:
        response = model.generate_content(prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=10000,
            temperature=0.7) , safety_settings=safe)

        return response.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return "Error: Unable to analyze manifest with AI."

# Start of the Execution 
def on_analyze(selected_appp):
    if selected_appp.get():
        selected_app = selected_appp.get()
        apk_path = get_app_path(selected_app)
        if apk_path:
            apk_filename = pull_apk(apk_path, selected_app)
            if apk_filename:
                decode_apk(apk_filename)
                manifest_data = parse_manifest(apk_filename)
                appinfo = app_info_entry.get()
                if manifest_data:
                    analysis = analyze_manifest_with_ai(manifest_data, appinfo)
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, analysis)
                    os.remove(apk_filename)
                    decoded_dir = f"{apk_filename}-decoded"
                    if os.path.exists(decoded_dir):
                        shutil.rmtree(decoded_dir)
    else:
        messagebox.showerror("Error", "No app selected!")

# Static Page
def show_static_analysis(apps):
    clear_frame()

    title_label = tk.Label(main_frame, text="Static Analysis - Android APK Analyzer", font=("Arial", 16))
    title_label.pack(pady=10)

    selected_appp = tk.StringVar()

    def on_text_hover(event):
        scroll_text.config(cursor="hand2")  # Change the cursor to a pointer on hover

    def on_text_leave(event):
        scroll_text.config(cursor="xterm")  # Reset the cursor when leaving the text area

    def on_text_click(event):
        index = scroll_text.index(f"@{event.x},{event.y}")  # Get the position of the click
        line_number = index.split('.')[0]  # Extract the line number
        line_text = scroll_text.get(f"{line_number}.0", f"{line_number}.end")  # Get the text of the entire line
        selected_appp.set(line_text.strip())  # Store the selected app
        entry.delete(0, tk.END)  # Clear the current text in the input box
        entry.insert(0, selected_appp.get())  # Set the input box text to the selected line
        print(f"Selected app: {selected_appp.get()}")

    scroll_text = scrolledtext.ScrolledText(main_frame, width=100, height=20, font=('Arial', 12), padx=10, pady=10)
    scroll_text.pack(padx=20, pady=20, ipadx=10, ipady=10)

    scroll_text.bind("<Button-1>", on_text_click)
    scroll_text.bind("<Motion>", on_text_hover)  # Change cursor when hovering over text
    scroll_text.bind("<Leave>", on_text_leave) 

    for app in apps:
        scroll_text.insert(tk.END, f"{app}\n")

    def update_listbox(event):
        typed_text = entry.get().lower()
        filtered_apps = [app for app in apps if typed_text in app.lower()]
        scroll_text.delete(1.0, tk.END)
        for app in filtered_apps:
            scroll_text.insert(tk.END, f"{app}\n")

    input_frame = tk.Frame(main_frame)
    input_frame.pack(pady=20)

    tk.Label(input_frame, text="Filter apps:", font=('Arial', 16)).pack(side=tk.LEFT, padx=10)
    entry = tk.Entry(input_frame)
    entry.pack(side=tk.LEFT, padx=10)
    entry.bind("<KeyRelease>", update_listbox)

    tk.Label(input_frame, text="Enter app details:", font=('Arial', 16)).pack(side=tk.LEFT, padx=5)
    global app_info_entry
    app_info_entry = tk.Entry(input_frame)
    app_info_entry.pack(side=tk.LEFT)

    analyze_button = tk.Button(main_frame, text="Analyze", command=lambda: on_analyze(selected_appp))
    analyze_button.pack(pady=10)

    back_button = tk.Button(main_frame, text="Back", command=show_initial_page)
    back_button.pack(pady=10)

    global result_text
    result_text = scrolledtext.ScrolledText(main_frame, width=200, height=100, font=("Arial", 16), padx=10, pady=10)
    result_text.pack(padx=20, pady=20)

    result_text.configure(wrap=tk.WORD, relief=tk.GROOVE, borderwidth=2)
    result_text.tag_configure("center", justify="center")
    result_text.insert(tk.END, "Analysis Results:\n", "center")

# Dynamic Page
def show_dynamic_analysis():
    clear_frame()

    title_label = tk.Label(main_frame, text="Dynamic Analysis - Android APK Analyzer", font=("Arial", 16))
    title_label.pack(pady=40)

    input_frame = tk.Frame(main_frame)
    input_frame.pack(pady=20)

    tk.Label(input_frame, text="Enter app details:", font=('Arial', 16)).pack(side=tk.LEFT, padx=5)
    global app_info_entrydyna
    app_info_entrydyna = tk.Entry(input_frame)
    app_info_entrydyna.pack(side=tk.LEFT)

    info_label = tk.Label(main_frame, text="Test the following data steal", font=("Arial", 14))
    info_label.pack(pady=10)

    # Add "Message" button
    message_button = tk.Button(main_frame, text="Message", command=handle_message)
    message_button.pack(pady=10)

    # Add "Other Audio" button
    audio_button = tk.Button(main_frame, text="Other Audio", command=handle_audio)
    audio_button.pack(pady=10)

    # Add "File" button
    file_button = tk.Button(main_frame, text="File", command=handle_file)
    file_button.pack(pady=10)

    # Back button
    back_button = tk.Button(main_frame, text="Back", command=show_initial_page)
    back_button.pack(pady=10)

    global result_text_dynamic
    result_text_dynamic = scrolledtext.ScrolledText(main_frame, width=200, height=100, font=("Arial", 16), padx=10, pady=10)
    result_text_dynamic.pack(padx=20, pady=20)

    result_text_dynamic.configure(wrap=tk.WORD, relief=tk.GROOVE, borderwidth=2)
    result_text_dynamic.tag_configure("center", justify="center")
    result_text_dynamic.insert(tk.END, "Analysis Results:\n", "center")

# Define the handlers for the buttons (you can customize these functions as per your requirement)
def handle_message():
    # Log the request (make sure this path is correct)
    # subprocess.Popen(["python3", "reqloger.py"])
    with open("requests.log", "w") as logfile:
        logfile.write("")
    message = "Your data is being captured"
    phone_number = "+9449334323"
    
    # Construct the ADB command
    command = ["adb", "emu", "sms", "send", phone_number, message]

    try:
        # Run the command
        subprocess.run(command, capture_output=True, text=True, check=True)
        t.sleep(2)
        appinfodyna = app_info_entrydyna.get()
        analyze_dynamicdata_with_ai(appinfodyna)
        print("Message sent successfully")

    except subprocess.CalledProcessError as e:
        print(f"Error sending message: {e.stderr}")
    except FileNotFoundError:
        print("Error: ADB command not found. Make sure ADB is installed and in your system PATH.")


def analyze_dynamicdata_with_ai(appinfodyna):
    model = genai.GenerativeModel('gemini-1.5-flash')
    safe = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]

    try:
        with open('requests.log', 'r') as file:
            content = file.read()

        prompt = (
            f" {content} analyze this para and give info and this app is about {appinfodyna} and find any data stealing and tell like a non cs student can understand"
        )

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=10000,
                temperature=0.7
            ),
            safety_settings=safe
        )

        result_text_dynamic.delete(1.0, tk.END)
        result_text_dynamic.insert(tk.END, response.candidates[0].content.parts[0].text)

        return response.candidates[0].content.parts[0].text

    except FileNotFoundError:
        print("Error: 'reqloger.py' file not found.")
        return "Error: Unable to read the log file."
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Error: {str(e)}"

def handle_audio():
    print("Other Audio button clicked")

def handle_file():
    print("File button clicked")


def show_initial_page():
    clear_frame()

    main_label = tk.Label(main_frame, text="APK Analyzer", font=("Arial", 18))
    main_label.pack(pady=30)

    static_button = tk.Button(main_frame, text="Static Analysis", command=lambda: show_static_analysis(get_installed_apps()), font=("Arial", 14))
    static_button.pack(pady=10)

    dynamic_button = tk.Button(main_frame, text="Dynamic Analysis", command=show_dynamic_analysis, font=("Arial", 14))
    dynamic_button.pack(pady=10)

def clear_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()

root = tk.Tk()
root.geometry("800x600")
root.title("APK Analyzer")

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

show_initial_page()

root.mainloop()
