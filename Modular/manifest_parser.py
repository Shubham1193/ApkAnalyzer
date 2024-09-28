import xml.etree.ElementTree as ET

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