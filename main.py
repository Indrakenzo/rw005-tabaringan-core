# ==============================================================================
# PROJECT: SI-WARGA TABARINGAN (CORE SYSTEM) - RW 005
# VERSION: 2.0 (Integrated Service & Information Hub)
# DEVELOPER: INDRAYAZA Z. (Junior Web Programmer & CLSOCA)
# LICENSE: GNU GPLv3 (Open Source for Public Service)
# ==============================================================================

from flask import Flask, render_template_string, request
from fpdf import FPDF
import datetime
import io
import base64

app = Flask(__name__)
app.secret_key = 'rw005_tabaringan_secure_v2'

# --- 1. CONFIG DATA PEJABAT (RW 05 TABARINGAN) ---
# Note: Data sensitif (Nomor HP) diset placeholder sampai izin diberikan.
PEJABAT = {
    "RW005": {
        "nama": "Rafiuddin Kasude",
        "jabatan": "Ketua RW 005",
        "alamat": "Tabaringan"
    },
    "RT001": {
        "nama": "Nurmala",
        "alamat": "Wilayah RT 001",
        "wa": "menunggu izin"
    },
    "RT002": {
        "nama": "Abd Muis",
        "alamat": "Wilayah RT 002",
        "wa": "menunggu izin"
    },
    "RT003": {
        "nama": "Syamsul Rijal",
        "alamat": "Wilayah RT 003",
        "wa": "menunggu izin"
    },
    "RT004": {
        "nama": "Abd. Rifai",
        "alamat": "Wilayah RT 004",
        "wa": "menunggu izin"
    }
}

# --- 2. FRONTEND (HTML + CSS BOOTSTRAP 5) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Warga RW 005 Tabaringan</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background-color: #f0f2f5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .hero-header { background: linear-gradient(135deg, #0d6efd, #0a58ca); color: white; padding: 40px 20px; border-radius: 0 0 30px 30px; margin-bottom: 30px; }
        .card-custom { border: none; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: transform 0.2s; }
        .card-custom:hover { transform: translateY(-3px); }
        .btn-emergency { font-weight: bold; padding: 12px; border-radius: 50px; text-transform: uppercase; letter-spacing: 1px; }
        .section-title { border-left: 5px solid #0d6efd; padding-left: 15px; margin-bottom: 20px; font-weight: 700; color: #2c3e50; }
        .security-badge { background-color: #e8f5e9; color: #2e7d32; padding: 10px; border-radius: 8px; font-size: 0.8rem; margin-top: 20px; }
    </style>
</head>
<body>

    <div class="hero-header text-center">
        <h1><i class="fas fa-landmark"></i> SI-WARGA RW 005</h1>
        <p class="mb-0">Kelurahan Tabaringan, Kec. Ujung Tanah</p>
        <small>Sistem Pelayanan Surat & Pusat Informasi Digital</small>
    </div>

    <div class="container pb-5">
        
        <div class="row mb-5">
            <div class="col-12">
                <h4 class="section-title text-danger"><i class="fas fa-ambulance"></i> DARURAT / EMERGENCY</h4>
                <div class="card card-custom p-3 bg-white">
                    <div class="row g-2">
                        <div class="col-md-4">
                            <a href="tel:112" class="btn btn-danger btn-emergency w-100 mb-2">
                                <i class="fas fa-user-md"></i> DOKTER KE RUMAH (112)
                            </a>
                            <small class="text-muted d-block text-center">Layanan Gratis Dottoro'ta (Cukup KTP)</small>
                        </div>
                        <div class="col-md-4">
                            <a href="tel:0411872228" class="btn btn-warning btn-emergency w-100 mb-2">
                                <i class="fas fa-tint"></i> PMI (STOK DARAH)
                            </a>
                            <small class="text-muted d-block text-center">Jl. Kandea (0411-872228)</small>
                        </div>
                        <div class="col-md-4">
                            <a href="https://www.instagram.com/baznasmakassar/" target="_blank" class="btn btn-success btn-emergency w-100 mb-2">
                                <i class="fas fa-ambulance"></i> AMBULANS BAZNAS
                            </a>
                            <small class="text-muted d-block text-center">Layanan Gratis untuk Dhuafa</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-6 mb-4">
                <h4 class="section-title text-primary"><i class="fas fa-info-circle"></i> INFO KESEJAHTERAAN</h4>
                
                <div class="accordion" id="accordionInfo">
                    <div class="accordion-item card-custom mb-2">
                        <h2 class="accordion-header">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse1">
                                <strong>🎓 INFO BEASISWA (SD - KULIAH)</strong>
                            </button>
                        </h2>
                        <div id="collapse1" class="accordion-collapse collapse show" data-bs-parent="#accordionInfo">
                            <div class="accordion-body small">
                                <ul>
                                    <li><strong>SD-SMA (PIP):</strong> Bantuan tunai. Cek di <a href="https://pip.kemdikbud.go.id">pip.kemdikbud.go.id</a>.</li>
                                    <li><strong>KIP Kuliah:</strong> Kuliah Gratis + Uang Saku. Daftar awal tahun di <a href="https://kip-kuliah.kemdikbud.go.id">kip-kuliah.kemdikbud.go.id</a>.</li>
                                    <li><strong>Beasiswa Kalla:</strong> Khusus Mahasiswa Sulsel Berprestasi/Dhuafa. Cek <a href="https://yayasanhadjikalla.or.id">yayasanhadjikalla.or.id</a>.</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <div class="accordion-item card-custom mb-2">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse2">
                                <strong>🏥 KESEHATAN & PELATIHAN KERJA</strong>
                            </button>
                        </h2>
                        <div id="collapse2" class="accordion-collapse collapse" data-bs-parent="#accordionInfo">
                            <div class="accordion-body small">
                                <ul>
                                    <li><strong>BPJS Gratis (UHC):</strong> Warga sakit tidak punya BPJS? Segera lapor Puskesmas Tabaringan untuk aktifkan UHC (Gratis via Pemkot).</li>
                                    <li><strong>Pelatihan Kerja (BLK):</strong> Kursus Las, Otomotif, Komputer Gratis. Lokasi: BLK Makassar (Jl. TMP).</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-6">
                <h4 class="section-title text-success"><i class="fas fa-print"></i> CETAK SURAT MANDIRI</h4>
                
                {% if success %}
                <div class="card card-custom bg-white text-center p-4">
                    <h1 class="display-4">✅</h1>
                    <h4 class="fw-bold">Surat Berhasil Dibuat!</h4>
                    <p class="text-muted">File PDF siap didownload.</p>
                    
                    <a href="data:application/pdf;base64,{{ pdf_data }}" download="Surat_{{ nama_warga }}.pdf" class="btn btn-primary btn-lg w-100 mb-2">
                        <i class="fas fa-download"></i> Download PDF
                    </a>
                    
                    {% if rt_wa_clean != '#' %}
                    <a href="https://wa.me/{{ rt_wa_clean }}" target="_blank" class="btn btn-success w-100">
                       <i class="fab fa-whatsapp"></i> Konfirmasi ke Ketua RT
                    </a>
                    {% else %}
                    <div class="alert alert-warning small mt-2">
                        Nomor WA Ketua RT belum tersedia di sistem. Silakan bawa surat ke rumah Beliau.
                    </div>
                    {% endif %}
                    
                    <a href="/" class="btn btn-link text-decoration-none mt-3">Buat Surat Baru</a>
                </div>

                {% else %}
                <div class="card card-custom bg-white p-4">
                    <form method="POST" action="/cetak">
                        <div class="mb-3">
                            <label class="form-label fw-bold">Pilih RT Domisili</label>
                            <select name="rt_pilihan" class="form-select" required>
                                <option value="" disabled selected>-- Pilih Ketua RT --</option>
                                {% for key, val in rt_list.items() if key != 'RW005' %}
                                <option value="{{ key }}">RT {{ key[-3:] }} - {{ val.nama }}</option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold">Jenis Keperluan</label>
                            <select name="jenis_surat" class="form-select" required>
                                <option value="Surat Pengantar KTP/KK">Pengantar KTP / KK</option>
                                <option value="Surat Pengantar SKCK">Pengantar SKCK (Kepolisian)</option>
                                <option value="Surat Keterangan Usaha">Keterangan Usaha (UMKM/Bank)</option>
                                <option value="Surat Keterangan Tidak Mampu">Keterangan Tidak Mampu (Bansos)</option>
                                <option value="Surat Keterangan Domisili">Keterangan Domisili Umum</option>
                            </select>
                        </div>
                        
                        <div class="row g-2 mb-3">
                            <div class="col-6">
                                <input type="text" name="nik" class="form-control" maxlength="16" placeholder="NIK (16 Digit)" required>
                            </div>
                            <div class="col-6">
                                <input type="text" name="kk" class="form-control" maxlength="16" placeholder="No. KK" required>
                            </div>
                        </div>

                        <div class="mb-3">
                            <input type="text" name="nama" class="form-control" placeholder="Nama Lengkap" required>
                        </div>
                        
                        <div class="row g-2 mb-3">
                            <div class="col-6">
                                <input type="text" name="tmp_lahir" class="form-control" placeholder="Tempat Lahir" required>
                            </div>
                            <div class="col-6">
                                <input type="date" name="tgl_lahir" class="form-control" required>
                            </div>
                        </div>

                        <div class="mb-3">
                            <input type="text" name="pekerjaan" class="form-control" placeholder="Pekerjaan" required>
                        </div>

                        <div class="mb-3">
                            <textarea name="alamat" class="form-control" rows="2" placeholder="Alamat Lengkap (Jl. Tabaringan...)" required></textarea>
                        </div>

                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary fw-bold"><i class="fas fa-print"></i> PROSES PDF</button>
                        </div>
                    </form>
                    
                    <div class="security-badge text-center">
                        <i class="fas fa-user-shield"></i> <strong>Privasi Terjamin</strong><br>
                        Sistem tidak menyimpan data NIK/KK Anda. Data langsung dihapus setelah PDF dicetak.
                    </div>
                </div>
                {% endif %}
            </div>
        </div>

        <div class="text-center mt-5 text-muted small">
            &copy; 2025 RW 005 Tabaringan Digital Core | Dev: Indrayaza Z.
        </div>
    </div>
</body>
</html>
"""

# --- 3. BACKEND LOGIC (PDF GENERATOR) ---
class PDF(FPDF):
    def header(self):
        # Kop Surat Standar Pemerintahan
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
    
    # Judul Surat
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, data['jenis_surat'].upper(), 0, 1, 'C')
    pdf.set_font("Arial", size=11)
    pdf.ln(5)

    # Isi Pembuka
    text_intro = "Yang bertanda tangan di bawah ini, Ketua RT dan Ketua RW 005 Kelurahan Tabaringan, Kecamatan Ujung Tanah, menerangkan dengan sebenarnya bahwa:"
    pdf.multi_cell(0, 6, text_intro)
    pdf.ln(5)

    # Biodata
    col_w = 45
    pdf.cell(col_w, 8, "Nama Lengkap", 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, data['nama'].upper(), 0, 1)
    pdf.cell(col_w, 8, "NIK / No. KTP", 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, data['nik'], 0, 1)
    pdf.cell(col_w, 8, "No. KK", 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, data['kk'], 0, 1)
    pdf.cell(col_w, 8, "Tempat/Tgl Lahir", 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, f"{data['tmp_lahir']}, {data['tgl_lahir']}", 0, 1)
    pdf.cell(col_w, 8, "Pekerjaan", 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, data['pekerjaan'], 0, 1)
    pdf.cell(col_w, 8, "Alamat", 0, 0); pdf.cell(5, 8, ":", 0, 0); pdf.cell(0, 8, data['alamat'], 0, 1)
    pdf.ln(5)

    # Penutup
    text_close = "Orang tersebut benar-benar adalah warga yang berdomisili di lingkungan kami. Surat pengantar ini diberikan untuk keperluan pengurusan administrasi sebagaimana mestinya."
    pdf.multi_cell(0, 6, text_close)
    pdf.ln(15)

    # Tanda Tangan
    tgl = datetime.datetime.now().strftime("%d-%m-%Y")
    
    # Posisi Tanda Tangan
    # Kiri: RW (Mengetahui)
    y_start = pdf.get_y()
    pdf.set_xy(10, y_start)
    pdf.cell(90, 5, "Mengetahui,", 0, 1, 'C')
    pdf.cell(90, 5, "Ketua RW 005", 0, 1, 'C')
    
    # Kanan: RT (Yang Bertanda Tangan)
    pdf.set_xy(110, y_start)
    pdf.cell(90, 5, f"Makassar, {tgl}", 0, 1, 'C')
    pdf.cell(90, 5, "Ketua RT " + data['rt_code'].replace("RT", ""), 0, 1, 'C')

    # Space Tanda Tangan
    pdf.ln(25)

    # Nama Pejabat
    pdf.set_xy(10, pdf.get_y())
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(90, 5, f"({PEJABAT['RW005']['nama']})", 0, 1, 'C') # Nama RW

    pdf.set_xy(110, pdf.get_y() - 5) # Align Y back
    pdf.cell(90, 5, f"({rt_data['nama']})", 0, 1, 'C') # Nama RT

    buffer = io.BytesIO()
    output = pdf.output(dest='S').encode('latin-1')
    buffer.write(output)
    buffer.seek(0)
    return buffer

# --- 4. FLASK ROUTES ---
@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE, success=False, rt_list=PEJABAT)

@app.route('/cetak', methods=['POST'])
def cetak():
    # Ambil data form
    data = {
        'rt_code': request.form['rt_pilihan'],
        'nik': request.form['nik'],
        'kk': request.form['kk'],
        'jenis_surat': request.form['jenis_surat'],
        'nama': request.form['nama'],
        'tmp_lahir': request.form['tmp_lahir'],
        'tgl_lahir': request.form['tgl_lahir'],
        'pekerjaan': request.form['pekerjaan'],
        'alamat': request.form['alamat']
    }
    
    rt_info = PEJABAT.get(data['rt_code'])
    
    # Logic WA
    raw_wa = rt_info.get('wa', '')
    if "menunggu" in raw_wa.lower() or raw_wa == "":
        nomor_bersih = "#"
    else:
        nomor_bersih = raw_wa.replace("-", "").replace(" ", "").replace("+", "")
        if nomor_bersih.startswith("0"):
            nomor_bersih = "62" + nomor_bersih[1:]

    # Buat PDF
    pdf_buffer = create_pdf_buffer(data, rt_info)
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

    return render_template_string(
        HTML_TEMPLATE, 
        success=True, 
        nama_warga=data['nama'], 
        pdf_data=pdf_base64, 
        rt_nama=rt_info['nama'], 
        rt_wa_clean=nomor_bersih,
        rt_list=PEJABAT
    )

# --- 5. RUN SERVER ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
