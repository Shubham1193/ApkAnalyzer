import google.generativeai as genai

# Configure the API key for Google Generative AI
genai.configure(api_key="AIzaSyC5NMftqNr1LeLSxPRDvfinai4LN5YpplQ")

def analyze_manifest_with_ai(manifest_data, appinfo):
    model = genai.GenerativeModel('gemini-1.5-flash')
    safe = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
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

def analyze_dynamic_data_with_ai(appinfo):
    model = genai.GenerativeModel('gemini-1.5-flash')
    safe = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    try:
        with open('requests.log', 'r') as file:
            content = file.read()

        prompt = (
            f"{content} analyze this para and give info and this app is about {appinfo} and find any data stealing and tell like a non cs student can understand this is a log from mobile making api request and just give info in very consize 100"
        )

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=10000,
                temperature=0.7
            ),
            safety_settings=safe
        )

        return response.candidates[0].content.parts[0].text

    except FileNotFoundError:
        print("Error: 'requests.log' file not found.")
        return "Error: Unable to read the log file."
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Error: {str(e)}"