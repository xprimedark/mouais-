from flask import Flask, request, render_template
from sheets_utils import reset_juice_column, update_juice_sales, load_start_time, save_start_time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print(">>> Flask démarre correctement")

app = Flask(__name__)
RESET_KEY = os.getenv("RESET_KEY")

@app.route("/")
def index():
    start_time = load_start_time()
    return render_template("index.html", start_time=start_time.strftime("%d/%m/%Y à %H:%M"), key=RESET_KEY)

@app.route("/log", methods=["POST"])
def receive_log():
    data = request.json
    update_juice_sales(data)
    return {"status": "ok"}, 200

@app.route("/reset", methods=["POST"])
def reset():
    key = request.form.get("key")
    if key != RESET_KEY:
        return "Clé invalide", 403
    reset_juice_column()
    save_start_time(datetime.now())
    return "Ventes réinitialisées avec succès !"

def start_flask():
    app.run(host="0.0.0.0", port=5000)

