import os
import subprocess
import base64
import json
from fastapi import FastAPI, Query
from pydantic import BaseModel
import openai
import shutil
import tempfile
from urllib.parse import unquote

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.get("/")
def home():
    return {"message": "RoboDict API is running!"}

@app.get("/compile")
async def compile_code(
    english_command: str = Query(..., description="Base64 encoded English command"),
    board: str = Query(..., description="Arduino board FQBN, e.g., arduino:avr:uno")
):
    print(f"Received request - english_command: {english_command}, board: {board}")  # Debug log
    
    try:
        # Decode the base64 encoded english command
        decoded_command = base64.b64decode(english_command).decode('utf-8')
        print(f"Decoded command: {decoded_command}")  # Debug log
    except Exception as e:
        return {"error": f"Failed to decode base64 English command: {str(e)}"}

    # 1. Ask OpenAI for code + explanation
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You convert English into Arduino sketches. Respond ONLY in valid JSON with keys: 'code' and 'explanation'. The code should be correct, with parsable json output, with correctly placed , classified unicode spaces , escapes. No error should occur while parsing the output to utf-8"},
                {"role": "user", "content": decoded_command}
            ]
        )
        content = response["choices"][0]["message"]["content"]
        print(f"OpenAI response: {content}")  # Debug log

        try:
            parsed = json.loads(content)
            code = parsed["code"]
            explanation = parsed["explanation"]
            code = code.encode("utf-8").decode("unicode_escape")
        except json.JSONDecodeError:
            return {"error": "Failed to parse model output", "raw": content}
    except Exception as e:
        return {"error": f"OpenAI API call failed: {str(e)}"}

    # 2. Save sketch in a fixed-name folder for Arduino CLI
    tmp_dir = tempfile.mkdtemp(prefix="arduino_")  # temp parent
    sketch_name = "sketch"  # fixed simple name
    sketch_dir = os.path.join(tmp_dir, sketch_name)
    os.makedirs(sketch_dir, exist_ok=True)
    sketch_path = os.path.join(sketch_dir, f"{sketch_name}.ino")
    try:
        with open(sketch_path, "w") as f:
            f.write(code)
    except Exception as e:
        return {"error": f"Failed to write sketch file: {str(e)}"}

    # 3. Compile with Arduino CLI
    build_dir = os.path.join(tmp_dir, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    cmd = [
        "arduino-cli",
        "compile",
        "--fqbn",
        board,
        "--output-dir",
        build_dir,
        "--verbose",
        sketch_dir
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # Added timeout
    except subprocess.TimeoutExpired:
        return {"error": "Compilation timeout"}
    except Exception as e:
        return {"error": f"Compilation process failed: {str(e)}"}

    # 4. Debug logs
    print("=== Arduino CLI STDOUT ===")
    print(result.stdout)
    print("=== Arduino CLI STDERR ===")
    print(result.stderr)

    if result.returncode != 0:
        return {"error": "Compilation failed", "stdout": result.stdout, "stderr": result.stderr}

    # 5. Locate HEX file
    hex_path = None
    try:
        for root, _, files in os.walk(build_dir):
            for f in files:
                if f.endswith(".hex"):
                    hex_path = os.path.join(root, f)
                    break
            if hex_path:
                break
    except Exception as e:
        return {"error": f"Error searching for HEX file: {str(e)}"}

    if not hex_path:
        return {"error": "HEX not found", "stdout": result.stdout, "stderr": result.stderr}

    # 6. Base64 encode HEX
    try:
        with open(hex_path, "rb") as f:
            hex_b64 = base64.b64encode(f.read()).decode()
    except Exception as e:
        return {"error": f"Failed to read and encode HEX file: {str(e)}"}

    # 7. Cleanup temp folder (optional)
    try:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    except:
        pass  # Ignore cleanup errors

    return {"code": code, "explanation": explanation, "hex": hex_b64}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))  # use Render's dynamic port
    uvicorn.run("server:app", host="0.0.0.0", port=port)
