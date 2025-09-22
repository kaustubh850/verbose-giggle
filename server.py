import os
import subprocess
import base64
from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class CompileRequest(BaseModel):
    english_command: str
    board: str

@app.post("/compile")
async def compile_code(req: CompileRequest):
    # 1. Generate Arduino code + explanation from OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that converts English commands to Arduino code."},
            {"role": "user", "content": req.english_command}
        ]
    )

    code = response["choices"][0]["message"]["content"]
    explanation = "Generated Arduino project based on your input."  # Could also be extracted from model if structured

    # 2. Save sketch file
    sketch_path = "/workspace/sketch/sketch.ino"
    os.makedirs("/workspace/sketch", exist_ok=True)
    with open(sketch_path, "w") as f:
        f.write(code)

    # 3. Compile with Arduino CLI
    cmd = [
        "arduino-cli", "compile",
        "--fqbn", req.board,
        "/workspace/sketch"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return {"error": "Compilation failed", "details": result.stderr}

    # 4. Find HEX file
    hex_path = "/workspace/sketch/build/{}.hex".format(req.board.replace(":", "."))
    if not os.path.exists(hex_path):
        return {"error": "HEX file not found"}

    # 5. Encode HEX to base64
    with open(hex_path, "rb") as f:
        hex_b64 = base64.b64encode(f.read()).decode()

    return {
        "code": code,
        "explanation": explanation,
        "hex": hex_b64
    }
