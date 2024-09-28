import subprocess

def get_installed_apps():
    try:
        result = subprocess.run(['adb', 'shell', 'pm', 'list', 'packages'], capture_output=True, text=True, check=True)
        packages = [line.split(":")[1] for line in result.stdout.splitlines()]
        return packages
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to list installed packages: {e}")
        return []

def get_app_path(package_name):
    try:
        result = subprocess.run(['adb', 'shell', 'pm', 'path', package_name], capture_output=True, text=True, check=True)
        apk_path = result.stdout.split(':')[1].strip()
        return apk_path
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to get the path for {package_name}: {e}")
        return None

def pull_apk(apk_path, package_name):
    try:
        filename = f"{package_name.split('.')[-1]}.apk"
        subprocess.run(['adb', 'pull', apk_path, filename], check=True)
        print(f"APK for {package_name} pulled successfully: {filename}")
        return filename
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to pull the APK for {package_name}: {e}")
        return None

def send_sms(phone_number, message):
    command = ["adb", "emu", "sms", "send", phone_number, message]
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        print("Message sent successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error sending message: {e.stderr}")
    except FileNotFoundError:
        print("Error: ADB command not found. Make sure ADB is installed and in your system PATH.")