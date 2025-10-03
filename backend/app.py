import os
import subprocess
import re
import google.generativeai as genai
import python_code_parse as pcp
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Serve the React frontend's static files in production
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)

# Configure the Gemini API key from an environment variable (the secure way)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=api_key)

# Define a dictionary for language-to-docker mapping
DOCKER_IMAGES = {
    'Python': {'image': 'python:3.9-slim', 'cmd': ['python', '-c']},
    'Java': {'image': 'openjdk:17-jdk-slim', 'cmd': ['sh', '-c', 'javac Main.java && java Main']},
    'C++': {'image': 'gcc:11-bullseye', 'cmd': ['sh', '-c', 'g++ main.cpp -o main && ./main']},
    'JavaScript': {'image': 'node:16-slim', 'cmd': ['node', '-e']}
}

# --- Module 1: Translation and Execution ---
def chunk_code_by_functions(code_string):
    """
    Splits a Python code string into a list of logical chunks (functions or global code).
    """
    try:
        function_infos = pcp.get_all_function_info_from_code(code_string)
        chunks = []
        last_line = 0
        for func_info in function_infos:
            start_line = func_info.line - 1
            end_line = func_info.end_line - 1
            function_code = "\n".join(code_string.splitlines()[start_line:end_line + 1])
            chunks.append(function_code)
            last_line = end_line + 1
        if last_line < len(code_string.splitlines()):
            remaining_code = "\n".join(code_string.splitlines()[last_line:])
            if remaining_code.strip():
                chunks.append(remaining_code)
        return chunks
    except Exception as e:
        print(f"Error during code chunking: {e}")
        return [code_string]

@app.route('/translate', methods=['POST'])
def translate_code():
    """ Main API endpoint for code translation. """
    data = request.json
    source_code = data.get('code')
    target_lang = data.get('language')
    if not source_code or not target_lang:
        return jsonify({'error': 'Missing code or language'}), 400

    full_translated_code = ""
    code_chunks = chunk_code_by_functions(code_string=source_code)
    
    if target_lang == 'Java':
        prompt_prefix = (
            f"You are an expert programmer. Translate the following Python code into {target_lang}. "
            "Ensure the code is contained within a class named 'Main' and includes a 'public static void main' method. "
            "Preserve the original logic. Do not include any extra explanations, just the translated code.\n\n"
        )
    else:
        prompt_prefix = (
            f"You are an expert programmer. Translate the following code snippet from its original language into {target_lang}. "
            "This is part of a larger file. Preserve the original logic and structure. "
            "Do not include any extra explanations, comments, or surrounding text, just the translated code.\n\n"
        )
        
    try:
        for chunk in code_chunks:
            prompt = prompt_prefix + f"```\n{chunk}\n```"
            response = genai.GenerativeModel('models/gemini-pro-latest').generate_content(prompt)
            translated_chunk = response.text.strip()
            full_translated_code += translated_chunk + "\n\n"
        return jsonify({'translated_code': full_translated_code})
    except Exception as e:
        print(f"An error occurred during API call: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/run_code', methods=['POST'])
def run_code():
    """ API endpoint to run user code in a secure Docker sandbox. """
    data = request.json
    code = data.get('code')
    target_lang = data.get('language')
    input_data = data.get('input', '')
    
    if not code or not target_lang:
        return jsonify({'error': 'No code or language provided'}), 400
    
    lang_config = DOCKER_IMAGES.get(target_lang)
    if not lang_config:
        return jsonify({'error': f"Unsupported language: {target_lang}"}), 400
    
    cleaned_code = re.sub(r'```[a-zA-Z]*\n|```', '', code).strip()

    if target_lang in ['Java', 'C++']:
        file_name = 'Main.java' if target_lang == 'Java' else 'main.cpp'
        volume_mount = f"{os.getcwd()}/temp_code:/app"
        os.makedirs("temp_code", exist_ok=True)
        with open(os.path.join("temp_code", file_name), 'w') as f:
            f.write(cleaned_code)
        docker_command = [
            "docker", "run", "--rm", "--network", "none",
            "-v", volume_mount, lang_config['image'], *lang_config['cmd']
        ]
    else:
        docker_command = [
            "docker", "run", "--rm", "--network", "none",
            lang_config['image'], *lang_config['cmd'], cleaned_code
        ]

    try:
        result = subprocess.run(
            docker_command, input=input_data, capture_output=True, text=True, timeout=20
        )
        return jsonify({
            'stdout': result.stdout, 'stderr': result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({'stdout': '', 'stderr': 'Error: Code execution timed out (20-second limit).'}), 408
    except Exception as e:
        print(f"An error occurred in run_code: {e}")
        return jsonify({'stdout': '', 'stderr': f'An unexpected error occurred: {str(e)}'}), 500




# --- Standard Flask Routes ---
@app.route('/')
def serve_react_app():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)

