# ==============================================================================
# PROJECT: SI-WARGA RW 05 (INTELLIGENCE & SURVEILLANCE EDITION)
# VERSION: 3.0 (News Feed + Access Logs)
# DEVELOPER: INDRAYAZA Z.
# ==============================================================================

import os
import logging
import datetime
import requests
import io
from flask import Flask, render_template, request, make_response
from fpdf import FPDF
from functools import wraps

app = Flask(__name__)

# --- CONFIGURATION ---
# 1. API KEY BERITA (Ganti dengan API Key Anda dari newsapi.org)
# Daftar gratis di: https://newsapi.org/register
NEWS_API_KEY = "a56068cbe59b4f20a1313afa5d796fcb" 
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# 2. KONFIGURASI LOGGING (SURVEILLANCE)
LOG_FOLDER = 'server_logs'
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

# Setup Logger
logging.basicConfig(
    filename=f'{LOG_FOLDER}/access_monitor.log',
    level=logging.INFO,
    format='%(asctime)s | IP: %(message)s'
)

# --- DATA PEJABAT ---
PEJABAT = {
    "RW005": {"nama": "Rafiuddin Kasude", "jabatan": "Ketua RW 005"},
    "RT001": {"nama": "Nurmala", "wa": "628xxxxxxx"},
    "RT002": {"nama": "Abd Muis", "wa": "628xxxxxxx"},
    "RT003": {"nama": "Syamsul Rijal", "wa": "628xxxxxxx"},
    "RT004": {"nama": "Abd. Rifai", "wa": "628xxxxxxx"}
}

# --- MODULE 1: SURVEILLANCE SYSTEM (LOGGER) ---
def log_visitor():
    """Mencatat siapa yang masuk ke dalam sistem"""
    # Mendapatkan IP Asli (support proxy/cloud)
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    
    user_agent = request.headers.get('User-Agent')
    path = request.path
    
    # Tulis ke file log
    log_message = f"{ip} | ACTION: {path} | DEVICE: {user_agent}"
    logging.info(log_message)
    print(f"[!] VISITOR DETECTED: {log_message}") # Print ke terminal juga

# --- MODULE 2: INTELLIGENCE FEED (NEWS) ---
def get_makassar_news():
    """Mengambil 3 berita terbaru tentang Makassar"""
    if NEWS_API_KEY == "GANTI_DENGAN_API_KEY_ANDA_DISINI":
        return [] # Return kosong jika API Key belum diisi

    params = {
        'q': 'Makassar OR "Sulawesi Selatan"', # Keyword pencarian
        'sortBy': 'publishedAt',
        'pageSize': 3, # Ambil 3 berita saja
        'apiKey': NEWS_API_KEY,
        'language': 'id' # Bahasa Indonesia
    }
    
    try:
        response = requests.get(NEWS_ENDPOINT, params=params, timeout=5)
        data = response.json()
        if data.get('status') == 'ok':
            return data.get('articles', [])
    except Exception as e:
        print(f"[ERROR] Gagal mengambil berita: {e}")
        return []
    
    return []

# --- MODULE 3: PDF GENERATOR ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 5, 'PEMERINTAH KOTA MAKASSAR', 0, 1, 'C')
        self.cell(0, 5, 'KECAMATAN UJUNG TANAH', 0, 1, 'C')
        self.set_font('Arial', 'B', 14)
        self.cell(0, 8, 'KELURAHAN TABARINGAN - RW 005', 0, 1, 'C')
        self.set_line_width(0.5)
        self.line(10, 28, 200, 28)
        self.ln(10)

def generate_pdf_buffer(data, rt_nama):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, data['jenis_surat'].upper(), 0, 1, 'C')
    pdf.set_font("Arial", size=11)
    pdf.ln(5)

    pdf.multi_cell(0, 6, "Yang bertanda tangan di bawah ini, Ketua RT dan Ketua RW 005 Kelurahan Tabaringan, menerangkan bahwa:")
    pdf.ln(5)

    fields = [("Nama Lengkap", data['nama'].upper()), ("NIK", data['nik']), ("No. KK", data['kk']), 
              ("TTL", f"{data['tmp_lahir']}, {data['tgl_lahir']}"), ("Pekerjaan", data['pekerjaan']), ("Alamat", data['alamat'])]

    for label, val in fields:
        pdf.cell(45, 8, label, 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, val, 0, 1)
    
    pdf.ln(5); pdf.multi_cell(0, 6, "Orang tersebut benar warga kami. Surat ini diberikan untuk keperluan administrasi."); pdf.ln(15)

    tgl = datetime.datetime.now().strftime("%d-%m-%Y")
    y_sig = pdf.get_y()
    pdf.set_xy(10, y_sig); pdf.cell(90, 5, "Mengetahui, Ketua RW 005", 0, 1, 'C')
    pdf.set_xy(110, y_sig); pdf.cell(90, 5, f"Makassar, {tgl}", 0, 1, 'C'); pdf.cell(90, 5, f"Ketua {data['rt_code'].replace('RT','RT ')}", 0, 1, 'C')
    pdf.ln(25)
    pdf.set_xy(10, pdf.get_y()); pdf.cell(90, 5, f"({PEJABAT['RW005']['nama']})", 0, 1, 'C')
    pdf.set_xy(110, pdf.get_y() - 5); pdf.cell(90, 5, f"({rt_nama})", 0, 1, 'C')

    output = io.BytesIO()
    output.write(pdf.output(dest='S').encode('latin-1'))
    output.seek(0)
    return output

# --- ROUTES ---
@app.route('/', methods=['GET'])
def index():
    # 1. Jalankan Logging
    log_visitor()
    
    # 2. Ambil Berita
    berita_list = get_makassar_news()
    
    return render_template('index.html', rt_list=PEJABAT, berita=berita_list)

@app.route('/cetak', methods=['POST'])
def cetak():
    log_visitor() # Log juga saat user mencetak surat
    form_data = request.form.to_dict()
    rt_info = PEJABAT.get(form_data['rt_code'])
    
    pdf_buffer = generate_pdf_buffer(form_data, rt_info['nama'])
    
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Surat_{form_data["nama"]}.pdf'
    return response

if __name__ == '__main__':
    # Auto-create log folder saat start
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    app.run(debug=True, port=8080)
