from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

app = Flask(__name__)

# ⚙️ Konfigurasi
app.config['SECRET_KEY'] = str(uuid.uuid4())
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'  # Ganti ke PostgreSQL kalau mau di Render
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🗃️ Model Database
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    to_addr = db.Column(db.String(150), nullable=False)
    from_addr = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(255), default='(Tanpa Subjek)')
    body = db.Column(db.Text, default='')
    received_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'to': self.to_addr,
            'from': self.from_addr,
            'subject': self.subject,
            'body': self.body,
            'received_at': self.received_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 🚀 Buat tabel otomatis
with app.app_context():
    db.create_all()

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
