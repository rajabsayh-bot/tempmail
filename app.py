from flask import Flask, render_template, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

# Simpan di memori (cukup buat tes)
EMAILS = []

@app.route('/')
def index():
    return render_template('index.html', emails=reversed(EMAILS))

@app.route('/api/receive', methods=['POST'])
def terima_email():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status":"gagal", "pesan":"data kosong"}), 400

        baru = {
            "id": len(EMAILS)+1,
            "to": data.get("to", ""),
            "from": data.get("from", ""),
            "subject": data.get("subject", "(Tanpa Subjek)"),
            "body": data.get("body", ""),
            "waktu": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        EMAILS.append(baru)
        return jsonify({"status":"sukses", "id":baru["id"]}), 200
    except Exception as e:
        return jsonify({"status":"error", "pesan":str(e)}), 500

@app.route('/api/list')
def daftar():
    return jsonify(list(reversed(EMAILS)))

@app.route('/api/lihat/<int:email_id>')
def lihat(email_id):
    for e in EMAILS:
        if e["id"] == email_id:
            return jsonify(e)
    return jsonify({"status":"tidak ada"}), 404

# Wajib buat Vercel
if __name__ == "__main__":
    app.run()
