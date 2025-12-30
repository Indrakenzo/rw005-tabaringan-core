# ==============================================================================
# PROJECT: SI-WARGA TABARINGAN (CORE SYSTEM) - RW 005
# DEVELOPER: INDRAYAZA Z. (Junior Web Programmer & CLSOCA)
# LICENSE: GNU GPLv3 (Open Source for Public Service)
# ==============================================================================

from flask import Flask, render_template, request, make_response
from fpdf import FPDF
import datetime
import io

app = Flask(__name__)

# --- DATA PEJABAT RW 005 ---
PEJABAT = {
    "RW005": {"nama": "Rafiuddin Kasude", "jabatan": "Ketua RW 005"},
    "RT001": {"nama": "Nurmala", "wa": "628xxxxxxxx"},
    "RT002": {"nama": "Abd Muis", "wa": "628xxxxxxxx"},
    "RT003": {"nama": "Syamsul Rijal", "wa": "628xxxxxxxx"},
    "RT004": {"nama": "Abd. Rifai", "wa": "628xxxxxxxx"}
}

# --- PDF GENERATOR ENGINE ---
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

def generate_pdf(data, rt_nama):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, data['jenis_surat'].upper(), 0, 1, 'C')
    pdf.set_font("Arial", size=11)
    pdf.ln(5)
    pdf.multi_cell(0, 6, "Yang bertanda tangan di bawah ini, Ketua RT dan Ketua RW 005 Kelurahan Tabaringan, menerangkan bahwa:")
    pdf.ln(5)
    fields = [("Nama", data['nama'].upper()), ("NIK", data['nik']), ("No. KK", data['kk']), 
              ("TTL", f"{data['tmp_lahir']}, {data['tgl_lahir']}"), ("Pekerjaan", data['pekerjaan']), ("Alamat", data['alamat'])]
    for label, val in fields:
        pdf.cell(45, 8, label, 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, val, 0, 1)
    pdf.ln(15)
    tgl = datetime.datetime.now().strftime("%d-%m-%Y")
    y_sig = pdf.get_y()
    pdf.set_xy(10, y_sig); pdf.cell(90, 5, "Mengetahui, Ketua RW 005", 0, 1, 'C')
    pdf.set_xy(110, y_sig); pdf.cell(90, 5, f"Makassar, {tgl}", 0, 1, 'C')
    pdf.ln(25)
    pdf.set_xy(10, pdf.get_y()); pdf.cell(90, 5, f"({PEJABAT['RW005']['nama']})", 0, 1, 'C')
    pdf.set_xy(110, pdf.get_y() - 5); pdf.cell(90, 5, f"({rt_nama})", 0, 1, 'C')
    output = io.BytesIO()
    output.write(pdf.output(dest='S').encode('latin-1'))
    output.seek(0)
    return output

@app.route('/')
def index():
    return render_template('index.html', rt_list=PEJABAT)

@app.route('/cetak', methods=['POST'])
def cetak():
    form_data = request.form.to_dict()
    rt_info = PEJABAT.get(form_data['rt_code'])
    pdf_buffer = generate_pdf(form_data, rt_info['nama'])
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Surat_{form_data["nama"]}.pdf'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
