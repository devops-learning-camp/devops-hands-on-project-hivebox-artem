# Version Printer App (Phase-02)

A minimal Python app that **prints the current application version and exits**.

## ✅ Current Version 0.0.1

## 🧱 Project Structure

├── app.py # prints version and exits
└── Dockerfile # container definition

## ▶️ Run Locally (without Docker)

```bash
python3 app.py
# Output:
# v0.0.1

Build the image:
docker build -t phase02/version-printer:0.0.1 .

Run the container:
docker run --rm phase02/version-printer:0.0.1
# Output:
# v0.0.1

Check exit code (should be 0):
docker run --rm phase02/version-printer:0.0.1 >/dev/null && echo "OK"

