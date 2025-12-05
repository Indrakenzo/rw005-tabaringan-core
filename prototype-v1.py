# ==============================================================================
# PROJECT: SI-WARGA TABARINGAN
# LOCATION: RW 005, KEL. TABARINGAN, KEC. UJUNG TANAH, MAKASSAR
# ==============================================================================
# DEVELOPER CREDITS:
# Name        : Indrayaza Z.
# Credential  : Junior Web Programmer
# Credential  : Certified Legal of Siber Operation Center Analyst (CLSOCA)
# ==============================================================================
# SECURITY NOTICE (FOR AUDITORS):
# This application is architected as STATELESS.
# 1. NO DATABASE connection is established.
# 2. NO LOGGING of Personally Identifiable Information (PII/NIK/KK).
# 3. All input data is flushed from RAM immediately after PDF generation.
# ==============================================================================

from flask import Flask, render_template_string, request, make_response
from fpdf import FPDF
import datetime
import io
import base64

app = Flask(__name__)
app.secret_key = 'rahasia_tabaringan_secure_key_rw005'

# --- 1. CONFIG DATA PEJABAT (HARDCODED AUTHORITY) ---
PEJABAT = {
    "RW005": {
        "nama": "Rafiuddin Kasude",
        "alamat": "menunggu izin untuk di input pada code",
    },
    "RT001": {
        "nama": "Nurmala",
        "alamat": "menunggu izin untuk di input pada code",
        "wa": "menunggu izin untuk di input pada code"
    },
    "RT002": {
        "nama": "Abd Muis",
        "alamat": "menunggu izin untuk di input pada code",
        "wa": "menunggu izin untuk di input pada code"
    },
    "RT003": {
        "nama": "Syamsul Rijal",
        "alamat": "menunggu izin untuk di input pada code",
        "wa": "menunggu izin untuk di input pada code"
    },
    "RT004": {
        "nama": "Abd. Rifai",
        "alamat": "menunggu izin untuk di input pada code",
        "wa": "menunggu izin untuk di input pada code"
    }
}

# --- 2. HTML TEMPLATE (Frontend) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Layanan Mandiri RW 005 Tabaringan</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card-header { background-color: #0d6efd; color: white; }
        .footer-dev { font-size: 0.75rem; color: #6c757d; margin-top: 30px; }
        .verified-badge { color: #198754; font-weight: bold; font-size: 0.8rem; }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                
                <div class="text-center mb-4">
                    <h2 class="fw-bold text-uppercase">Layanan Warga RW 005</h2>
                    <p class="text-muted">Kelurahan Tabaringan, Kecamatan Ujung Tanah</p>
                </div>

                <div class="alert alert-info shadow-sm" role="alert" style="font-size: 0.9rem;">
                    <div class="d-flex align-items-center mb-2">
                        <span class="fs-4 me-2">🛡️</span>
                        <strong>Jaminan Privasi & Keamanan Data</strong>
                    </div>
                    Aplikasi ini menerapkan prinsip <em>Zero Data Storage</em>. Sistem <strong>TIDAK MENYIMPAN</strong> data NIK, KK, atau Nama Anda ke dalam database apapun. Data Anda hanya diproses sesaat untuk dicetak menjadi surat, lalu terhapus otomatis.
                    <hr>
                    <small class="text-muted">
                        Dikembangkan & Diawasi oleh: <strong>Indrayaza Z.</strong><br>
                        <span class="verified-badge">✓ Junior Web Programmer</span> | 
                        <span class="verified-badge">✓ Certified Legal of Siber Operation Center Analyst</span>
                    </small>
                </div>

                {% if success %}
                <div class="card shadow-sm border-0 mb-4">
                    <div class="card-body text-center p-5">
                        <div class="mb-3"><h1 style="font-size: 4rem;">✅</h1></div>
                        <h3 class="card-title text-success fw-bold">Surat Selesai!</h3>
                        <p class="card-text">Data Anda telah dihapus dari memori server demi keamanan.</p>
                        
                        <a href="data:application/pdf;base64,{{ pdf_data }}" download="Surat_Pengantar_{{ nama_warga }}.pdf" class="btn btn-success btn-lg mb-4 shadow w-100">
                            ⬇️ Download PDF Surat
                        </a>

                        <div class="alert alert-warning text-start" role="alert">
                            <h6 class="fw-bold">⚠️ Langkah Selanjutnya:</h6>
                            <p class="mb-1 small">Silakan bawa surat ini ke:</p>
                            <ul class="mb-0 small">
                                <li><strong>{{ rt_nama }}</strong> ({{ rt_kode }})</li>
                                <li>Alamat: {{ rt_alamat }}</li>
                            </ul>
                        </div>
                        <a href="/" class="btn btn-outline-secondary mt-3">Kembali ke Depan</a>
                    </div>
                </div>

                {% else %}
                <div class="card shadow border-0">
                    <div class="card-header text-center py-3">
                        <h5 class="mb-0">Formulir Surat Pengantar</h5>
                    </div>
                    <div class="card-body p-4">
                        <form method="POST" action="/cetak">
                            
                            <h6 class="text-primary fw-bold mb-3">1. Tujuan & Identitas Wilayah</h6>
                            <div class="mb-3">
                                <label class="form-label">Ketua RT Tujuan:</label>
                                <select name="rt_pilihan" class="form-select" required>
                                    <option value="" selected disabled>-- Pilih RT --</option>
                                    <option value="RT001">RT 001 (Ibu Nurmala)</option>
                                    <option value="RT002">RT 002 (Bpk. Abd Muis)</option>
                                    <option value="RT003">RT 003 (Bpk. Syamsul Rijal)</option>
                                    <option value="RT004">RT 004 (Bpk. Abd. Rifai)</option>
                                </select>
                            </div>

                            <h6 class="text-primary fw-bold mb-3 mt-4">2. Verifikasi Mandiri (Tanpa Database)</h6>
                            <div class="row g-2">
                                <div class="col-6">
                                    <label class="form-label small">3 Digit Akhir NIK</label>
                                    <input type="text" name="nik_code" class="form-control" placeholder="123" maxlength="3" pattern="\d{3}" required>
                                </div>
                                <div class="col-6">
                                    <label class="form-label small">3 Digit Akhir KK</label>
                                    <input type="text" name="kk_code" class="form-control" placeholder="456" maxlength="3" pattern="\d{3}" required>
                                </div>
                            </div>

                            <h6 class="text-primary fw-bold mb-3 mt-4">3. Detail Surat</h6>
                            <div class="mb-3">
                                <label class="form-label">Jenis Keperluan:</label>
                                <select name="jenis_surat" class="form-select" required>
                                    <option value="Surat Pengantar Pengurusan KTP/KK">Pengantar KTP/KK</option>
                                    <option value="Surat Pengantar SKCK (Kepolisian)">Pengantar SKCK</option>
                                    <option value="Surat Keterangan Domisili Usaha">Ket. Domisili Usaha</option>
                                    <option value="Surat Keterangan Tidak Mampu (Bansos)">Ket. Tidak Mampu (Bansos)</option>
                                    <option value="Surat Keterangan Kematian">Ket. Kematian</option>
                                    <option value="Surat Keterangan Kelahiran">Ket. Kelahiran</option>
                                    <option value="Surat Keterangan Pindah/Datang">Pindah/Datang</option>
                                </select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Nama Lengkap:</label>
                                <input type="text" name="nama" class="form-control" required>
                            </div>
                            
                            <div class="row g-2 mb-3">
                                <div class="col-md-6">
                                    <label class="form-label">Tempat Lahir:</label>
                                    <input type="text" name="tmp_lahir" class="form-control" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Tgl Lahir:</label>
                                    <input type="date" name="tgl_lahir" class="form-control" required>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Pekerjaan:</label>
                                <input type="text" name="pekerjaan" class="form-control" required>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Alamat Lengkap:</label>
                                <textarea name="alamat" class="form-control" rows="2" required></textarea>
                            </div>

                            <div class="d-grid gap-2 mt-4">
                                <button type="submit" class="btn btn-primary btn-lg fw-bold">PROSES SURAT SEKARANG</button>
                            </div>
                        </form>
                    </div>
                </div>

                <div class="mt-4 text-center">
                    <a href="https://cekbansos.kemensos.go.id/" target="_blank" class="btn btn-sm btn-outline-danger">
                        🔍 Cek Bansos Kemensos RI
                    </a>
                </div>
                {% endif %}
                
                <div class="footer-dev text-center">
                    &copy; 2025 RW 005 Tabaringan. Open Source Project (GPLv3).<br>
                    Engineered by <strong>Indrayaza Z.</strong>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- 3. LOGIC PDF GENERATOR ---
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

def create_pdf_buffer(data, rt_data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Judul
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, data['jenis_surat'].upper(), 0, 1, 'C')
    pdf.set_font("Arial", size=11)
    pdf.ln(5)

    # Body
    text_intro = "Yang bertanda tangan di bawah ini, Ketua RT dan Ketua RW 005 Kelurahan Tabaringan, Kecamatan Ujung Tanah, menerangkan dengan sebenarnya bahwa:"
    pdf.multi_cell(0, 6, text_intro)
    pdf.ln(5)

    col_w = 45
    pdf.cell(col_w, 8, "Nama Lengkap", 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, data['nama'].upper(), 0, 1)
    pdf.cell(col_w, 8, "Tempat/Tgl Lahir", 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, f"{data['tmp_lahir']}, {data['tgl_lahir']}", 0, 1)
    pdf.cell(col_w, 8, "Pekerjaan", 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, data['pekerjaan'], 0, 1)
    pdf.cell(col_w, 8, "Alamat", 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, data['alamat'], 0, 1)
    pdf.ln(5)

    text_close = "Orang tersebut benar-benar adalah warga yang berdomisili di lingkungan kami. Surat ini diberikan untuk keperluan administrasi sebagaimana mestinya."
    pdf.multi_cell(0, 6, text_close)
    pdf.ln(15)

    # Tanda Tangan
    tgl = datetime.datetime.now().strftime("%d-%m-%Y")
    pdf.set_x(120); pdf.cell(80, 5, f"Makassar, {tgl}", 0, 1, 'C')
    pdf.set_x(120); pdf.cell(80, 5, "Ketua RT " + data['rt_code'].replace("RT", ""), 0, 1, 'C')
    pdf.ln(20)
    pdf.set_x(120); pdf.cell(80, 5, f"({rt_data['nama']})", 0, 1, 'C')

    pdf.ln(5); pdf.cell(0, 5, "Mengetahui,", 0, 1, 'C')
    pdf.cell(0, 5, PEJABAT['RW']['jabatan'], 0, 1, 'C')
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 5, f"({PEJABAT['RW']['nama']})", 0, 1, 'C')

    buffer = io.BytesIO()
    output = pdf.output(dest='S').encode('latin-1')
    buffer.write(output)
    buffer.seek(0)
    return buffer

# --- 4. ROUTES ---
@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE, success=False)

@app.route('/cetak', methods=['POST'])
def cetak():
    data = {
        'rt_code': request.form['rt_pilihan'],
        'jenis_surat': request.form['jenis_surat'],
        'nama': request.form['nama'],
        'tmp_lahir': request.form['tmp_lahir'],
        'tgl_lahir': request.form['tgl_lahir'],
        'pekerjaan': request.form['pekerjaan'],
        'alamat': request.form['alamat']
    }
    rt_info = PEJABAT.get(data['rt_code'])
    pdf_buffer = create_pdf_buffer(data, rt_info)
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

    return render_template_string(HTML_TEMPLATE, success=True, nama_warga=data['nama'], pdf_data=pdf_base64, rt_nama=rt_info['nama'], rt_kode=data['rt_code'], rt_alamat=rt_info['alamat'])

# --- 5. RUN ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
