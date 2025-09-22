import os
import subprocess
import base64
import json
from fastapi import FastAPI
from pydantic import BaseModel
import openai
import shutil
import tempfile

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.get("/")
def home():
    return {"message": "RoboDict API is running!"}

class CompileRequest(BaseModel):
    english_command: str
    board: str  # e.g. "arduino:avr:uno"

@app.post("/compile")
async def compile_code(req: CompileRequest):

    # 1. Ask OpenAI for code + explanation
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You convert English into Arduino sketches. Respond ONLY in valid JSON with keys: 'code' and 'explanation'."},
            {"role": "user", "content": req.english_command}
        ]
    )
    content = response["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(content)
        code = parsed["code"]
        explanation = parsed["explanation"]
    except json.JSONDecodeError:
        return {"error": "Failed to parse model output", "raw": content}

    # 2. Save sketch in a fixed-name folder for Arduino CLI
    tmp_dir = tempfile.mkdtemp(prefix="arduino_")  # temp parent
    sketch_name = "sketch"  # fixed simple name
    sketch_dir = os.path.join(tmp_dir, sketch_name)
    os.makedirs(sketch_dir, exist_ok=True)
    sketch_path = os.path.join(sketch_dir, f"{sketch_name}.ino")
    with open(sketch_path, "w") as f:
        f.write(code)

    # 3. Compile with Arduino CLI
    build_dir = os.path.join(tmp_dir, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    cmd = [
        "arduino-cli",
        "compile",
        "--fqbn",
        req.board,
        "--output-dir",
        build_dir,
        "--verbose",
        sketch_dir
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # 4. Debug logs
    print("=== Arduino CLI STDOUT ===")
    print(result.stdout)
    print("=== Arduino CLI STDERR ===")
    print(result.stderr)

    if result.returncode != 0:
        return {"error": "Compilation failed", "stdout": result.stdout, "stderr": result.stderr}

    # 5. Locate HEX file
    hex_path = None
    for root, _, files in os.walk(build_dir):
        for f in files:
            if f.endswith(".hex"):
                hex_path = os.path.join(root, f)
                break
        if hex_path:
            break

    if not hex_path:
        return {"error": "HEX not found", "stdout": result.stdout, "stderr": result.stderr}

    # 6. Base64 encode HEX
    with open(hex_path, "rb") as f:
        hex_b64 = base64.b64encode(f.read()).decode()

    # 7. Cleanup temp folder (optional)
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return {"code": code, "explanation": explanation, "hex": hex_b64}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))  # use Render’s dynamic port
    uvicorn.run("server:app", host="0.0.0.0", port=port)
