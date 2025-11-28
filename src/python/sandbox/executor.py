from flask import Flask, request, jsonify
import subprocess
import tempfile

app = Flask(__name__)

@app.post("/run")
def run():
    data = request.get_json()
    code = data.get("code", "")

    # Write code to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        path = f.name

    try:
        result = subprocess.run(
            ["python3", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return jsonify({
            "stdout": result.stdout.decode(),
            "stderr": result.stderr.decode()
        })

    except subprocess.TimeoutExpired:
        return jsonify({"stdout": "", "stderr": "Error: timeout reached"}), 408

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
