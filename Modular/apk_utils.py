import subprocess
import os
import shutil

def decode_apk(apk_filename):
    try:
        subprocess.run(['java', '-jar', 'apktool.jar', 'd', apk_filename, '-o', f"{apk_filename}-decoded"], check=True)
        print(f"APK decoded successfully: {apk_filename}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to decode the APK: {e}")

def cleanup_apk_files(apk_filename):
    try:
        os.remove(apk_filename)
        decoded_dir = f"{apk_filename}-decoded"
        if os.path.exists(decoded_dir):
            shutil.rmtree(decoded_dir)
        print(f"Cleaned up APK files for: {apk_filename}")
    except Exception as e:
        print(f"An error occurred while cleaning up APK files: {e}")