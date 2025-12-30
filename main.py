# ==============================================================================
# PROJECT: SI-WARGA TABARINGAN (CORE SYSTEM) - RW 005
# DEVELOPER: INDRAYAZA Z. (Junior Web Programmer & CLSOCA)
# LICENSE: GNU GPLv3 (Open Source for Public Service)
# ==============================================================================

import os
import datetime
import requests
import io
import base64
from flask import Flask, render_template, request, make_response
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'rw005_tabaringan_secure_v4'

# --- CONFIGURATION ---
# Masukkan API Key Anda di sini
NEWS_API_KEY = "a56068cbe59b4f20a1313afa5d796fcb" 

PEJABAT = {
    "RW005": {"nama": "Rafiuddin Kasude", "jabatan": "Ketua RW 005"},
    "RT001": {"nama": "Nurmala", "alamat": "Tabaringan", "wa": ""},
    "RT002": {"nama": "Abd Muis", "alamat": "Tabaringan", "wa": ""},
    "RT003": {"nama": "Syamsul Rijal", "alamat": "Tabaringan", "wa": ""},
    "RT004": {"nama": "Abd. Rifai", "alamat": "Tabaringan", "wa": ""}
}

# --- PDF ENGINE ---
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

@app.route('/')
def index():
    # Fetch News
    berita = []
    if NEWS_API_KEY != "a56068cbe59b4f20a1313afa5d796fcb":
        try:
            url = f"https://newsapi.org/v2/everything?q=Makassar&sortBy=publishedAt&pageSize=3&apiKey={NEWS_API_KEY}&language=id"
            res = requests.get(url, timeout=5)
            berita = res.json().get('articles', [])
        except: berita = []
    
    return render_template('index.html', rt_list=PEJABAT, berita=berita)

@app.route('/cetak', methods=['POST'])
def cetak():
    data = request.form
    rt_info = PEJABAT.get(data['rt_code'])
    
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, data['jenis_surat'].upper(), 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 6, "Menerangkan dengan sebenarnya bahwa warga di bawah ini:")
    pdf.ln(3)
    
    fields = [("Nama", data['nama'].upper()), ("NIK", data['nik']), ("Alamat", data['alamat'])]
    for l, v in fields:
        pdf.cell(40, 8, l, 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, v, 0, 1)
        
    pdf.ln(10)
    pdf.cell(0, 5, f"Makassar, {datetime.date.today().strftime('%d-%m-%Y')}", 0, 1, 'R')
    pdf.ln(20)
    pdf.cell(90, 5, f"({PEJABAT['RW005']['nama']})", 0, 0, 'C')
    pdf.cell(90, 5, f"({rt_info['nama']})", 0, 1, 'C')

    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Surat_{data["nama"]}.pdf'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
