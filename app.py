from flask import Flask, render_template, request, jsonify
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)

# ⚙️ Konfigurasi
app.config['SECRET_KEY'] = str(uuid.uuid4())

# 🗃️ Simpan data pakai variabel memori (cocok buat tes)
# Catatan: Data hilang kalau Vercel "tidur" / deploy ulang
EMAILS = []

# 📄 Halaman Utama
@app.route('/')
def index():
    return render_template('index.html', emails=EMAILS[::-1])

# 📩 API Terima Email dari Cloudflare
@app.route('/api/receive', methods=['POST'])
def terima_email():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'gagal', 'pesan': 'Data kosong'}), 400

        surat_baru = {
            'id': len(EMAILS) + 1,
            'to': data.get('to', ''),
            'from': data.get('from', ''),
            'subject': data.get('subject', '(Tanpa Subjek)'),
            'body': data.get('body', ''),
            'received_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }

        EMAILS.append(surat_baru)
        return jsonify({'status': 'sukses', 'id': surat_baru['id']}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'pesan': str(e)}), 500

# 📡 API Baca Data
@app.route('/api/list', methods=['GET'])
def daftar_email():
    return jsonify(EMAILS[::-1])

@app.route('/api/lihat/<int:email_id>', methods=['GET'])
def lihat_email(email_id):
    for surat in EMAILS:
        if surat['id'] == email_id:
            return jsonify(surat)
    return jsonify({'status': 'tidak ditemukan'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# 📄 Halaman Utama
@app.route('/')
def index():
    daftar_email = Email.query.order_by(Email.received_at.desc()).all()
    return render_template('index.html', emails=daftar_email)

# 📩 API Terima Data dari Cloudflare Worker
@app.route('/api/receive', methods=['POST'])
def terima_email():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'gagal', 'pesan': 'Data kosong'}), 400

    baru = Email(
        to_addr = data.get('to', ''),
        from_addr = data.get('from', ''),
        subject = data.get('subject', ''),
        body = data.get('body', '')
    )
    db.session.add(baru)
    db.session.commit()
    return jsonify({'status': 'sukses', 'id': baru.id}), 200

# 📡 API Ambil Data (buat otomatisasi/MacroDroid)
@app.route('/api/list', methods=['GET'])
def daftar_email():
    semua = Email.query.order_by(Email.received_at.desc()).all()
    return jsonify([e.to_dict() for e in semua])

@app.route('/api/lihat/<int:email_id>', methods=['GET'])
def lihat_email(email_id):
    surat = Email.query.get_or_404(email_id)
    return jsonify(surat.to_dict())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
