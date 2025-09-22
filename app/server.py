import os
import subprocess
import base64
import json
from fastapi import FastAPI
from pydantic import BaseModel
import openai

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
    # 1. Ask OpenAI for code + explanation (JSON structured)
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You convert English into Arduino sketches. "
                    "Respond ONLY in valid JSON with keys: 'code' and 'explanation'."
                )
            },
            {"role": "user", "content": req.english_command}
        ]
    )

    content = response["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(content)   # safe JSON parser
        code = parsed["code"]
        explanation = parsed["explanation"]
    except json.JSONDecodeError:
        return {"error": "Failed to parse model output", "raw": content}

    # 2. Save sketch
    sketch_dir = "/workspace/sketch"
    os.makedirs(sketch_dir, exist_ok=True)
    sketch_path = os.path.join(sketch_dir, "sketch.ino")
    with open(sketch_path, "w") as f:
        f.write(code)

    # 3. Compile with Arduino CLI
    cmd = ["arduino-cli", "compile", "--fqbn", req.board, sketch_dir]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return {
            "error": "Compilation failed",
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    # 4. Locate HEX file
    build_dir = os.path.join(sketch_dir, "build", req.board.replace(":", "."))
    hex_path = os.path.join(build_dir, "sketch.ino.hex")
    if not os.path.exists(hex_path):
        return {"error": "HEX not found", "details": build_dir}

    # 5. Base64 encode HEX
    with open(hex_path, "rb") as f:
        hex_b64 = base64.b64encode(f.read()).decode()

    return {
        "code": code,
        "explanation": explanation,
        "hex": hex_b64
    }
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))  # use Render’s dynamic port
    uvicorn.run("server:app", host="0.0.0.0", port=port)
