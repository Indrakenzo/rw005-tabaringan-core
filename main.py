# ==============================================================================
# PROJECT: SI-WARGA TABARINGAN (CORE SYSTEM) - RW 005
# DEVELOPER: INDRAYAZA Z. (Junior Web Programmer & CLSOCA)
# LICENSE: GNU GPLv3 (Open Source for Public Service)
# ==============================================================================

from flask import Flask, render_template_string, request
from fpdf import FPDF
import datetime
import io
import base64

app = Flask(__name__)
app.secret_key = 'rw005_tabaringan_secure'

# --- 1. CONFIG DATA PEJABAT (PEMBARUAN: DATA SEMENTARA) ---
# Data alamat dan WA diset "menunggu izin" demi privasi
PEJABAT = {
    "RW005": {
        "nama": "Rafiuddin Kasude",
        "jabatan": "Ketua RW 005",
        "alamat": "menunggu izin untuk di input pada code"
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

# --- 2. FRONTEND (HTML + CSS BOOTSTRAP) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Layanan RW 005 Tabaringan</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: sans-serif; }
        .header-title { color: #2c3e50; font-weight: bold; }
        .security-badge { background-color: #e8f5e9; color: #2e7d32; padding: 10px; border-radius: 8px; border: 1px solid #c8e6c9; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                
                <div class="text-center mb-4">
                    <h2 class="header-title">SI-WARGA RW 005</h2>
                    <p class="text-muted">Kelurahan Tabaringan, Kec. Ujung Tanah</p>
                </div>

                <div class="security-badge mb-4 text-center">
                    🔒 <strong>Jaminan Privasi (Stateless System)</strong><br>
                    Sistem ini TIDAK MENYIMPAN data pribadi (NIK/KK) Anda. Data langsung dihapus otomatis setelah surat dicetak.
                    <br><small class="text-muted">Dev: Indrayaza Z.</small>
                </div>

                {% if success %}
                <div class="card shadow border-0 text-center p-4">
                    <h1 class="display-1">✅</h1>
                    <h3 class="text-success fw-bold">Surat Siap!</h3>
                    <p>Silakan download surat, lalu kabari Ketua RT.</p>
                    
                    <a href="data:application/pdf;base64,{{ pdf_data }}" download="Surat_{{ nama_warga }}.pdf" class="btn btn-primary btn-lg mb-3 w-100">
                        ⬇️ Download PDF Surat
                    </a>

                    {% if rt_wa_clean != '#' %}
                    <a href="https://wa.me/{{ rt_wa_clean }}?text=Assalamu'alaikum%20Bpk/Ibu%20{{ rt_nama }},%20saya%20{{ nama_warga }}.%20Saya%20sudah%20cetak%20surat%20pengantar%20mandiri." 
                       target="_blank" class="btn btn-success fw-bold w-100 mb-3">
                       📞 Chat WA Ketua RT (Konfirmasi)
                    </a>
                    {% else %}
                    <button class="btn btn-secondary w-100 mb-3" disabled>
                       📞 Kontak WA Belum Tersedia (Hubungi Langsung)
                    </button>
                    {% endif %}

                    <div class="alert alert-warning text-start small">
                        <strong>Info Alamat:</strong><br>
                        Rumah Bpk/Ibu {{ rt_nama }}<br>
                        {{ rt_alamat }}
                    </div>
                    
                    <a href="/" class="btn btn-outline-secondary btn-sm">Kembali ke Depan</a>
                </div>

                {% else %}
                <div class="card shadow-sm border-0">
                    <div class="card-body p-4">
                        <form method="POST" action="/cetak">
                            <h5 class="text-primary mb-3">1. Pilih Tujuan</h5>
                            <div class="mb-3">
                                <label class="form-label">Ketua RT Domisili:</label>
                                <select name="rt_pilihan" class="form-select" required>
                                    <option value="" disabled selected>-- Pilih RT --</option>
                                    <option value="RT001">RT 001 (Ibu Nurmala)</option>
                                    <option value="RT002">RT 002 (Bpk. Abd Muis)</option>
                                    <option value="RT003">RT 003 (Bpk. Syamsul Rijal)</option>
                                    <option value="RT004">RT 004 (Bpk. Abd. Rifai)</option>
                                </select>
                            </div>

                            <h5 class="text-primary mb-3 mt-4">2. Isi Data Surat</h5>
                            <div class="mb-3">
                                <label class="form-label">Keperluan:</label>
                                <select name="jenis_surat" class="form-select" required>
                                    <option value="Surat Pengantar KTP/KK">Pengantar KTP/KK</option>
                                    <option value="Surat Pengantar SKCK">Pengantar SKCK</option>
                                    <option value="Surat Keterangan Usaha">Ket. Domisili Usaha</option>
                                    <option value="Surat Keterangan Tidak Mampu">Ket. Tidak Mampu (Bansos)</option>
                                    <option value="Surat Keterangan Domisili">Ket. Domisili Biasa</option>
                                </select>
                            </div>
                            
                            <div class="row g-2 mb-3">
                                <div class="col-6">
                                    <label class="form-label">NIK (16 Digit):</label>
                                    <input type="text" name="nik" class="form-control" maxlength="16" pattern="\d{16}" placeholder="Angka NIK Lengkap" required>
                                </div>
                                <div class="col-6">
                                    <label class="form-label">No. KK (16 Digit):</label>
                                    <input type="text" name="kk" class="form-control" maxlength="16" pattern="\d{16}" placeholder="Angka KK Lengkap" required>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Nama Lengkap:</label>
                                <input type="text" name="nama" class="form-control" required>
                            </div>
                            
                            <div class="row g-2 mb-3">
                                <div class="col-6">
                                    <label class="form-label">Tempat Lahir:</label>
                                    <input type="text" name="tmp_lahir" class="form-control" required>
                                </div>
                                <div class="col-6">
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
                                <textarea name="alamat" class="form-control" rows="2" placeholder="Jl. Tabaringan..." required></textarea>
                            </div>

                            <div class="d-grid gap-2 mt-4">
                                <button type="submit" class="btn btn-primary fw-bold">PROSES CETAK PDF</button>
                            </div>
                        </form>
                    </div>
                </div>

                <div class="text-center mt-4 mb-5">
                    <a href="https://cekbansos.kemensos.go.id/" target="_blank" class="btn btn-sm btn-outline-danger">🔍 Cek Bansos Kemensos</a>
                    <p class="mt-3 small text-muted">&copy; 2025 RW 005 Tabaringan Core</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- 3. BACKEND LOGIC (PDF GENERATOR) ---
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
    
    # Kanan: RT
    pdf.set_x(120); pdf.cell(80, 5, f"Makassar, {tgl}", 0, 1, 'C')
    pdf.set_x(120); pdf.cell(80, 5, "Ketua RT " + data['rt_code'].replace("RT", ""), 0, 1, 'C')
    pdf.ln(20)
    pdf.set_x(120); pdf.cell(80, 5, f"({rt_data['nama']})", 0, 1, 'C')

    # Tengah Bawah: RW (Update Key ke RW005)
    pdf.ln(5); pdf.cell(0, 5, "Mengetahui,", 0, 1, 'C')
    pdf.cell(0, 5, PEJABAT['RW005']['jabatan'], 0, 1, 'C')
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 5, f"({PEJABAT['RW005']['nama']})", 0, 1, 'C')

    buffer = io.BytesIO()
    output = pdf.output(dest='S').encode('latin-1')
    buffer.write(output)
    buffer.seek(0)
    return buffer

# --- 4. FLASK ROUTES ---
@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE, success=False)

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
    
    # Logic WA: Cek apakah data sudah diizinkan atau masih placeholder
    raw_wa = rt_info.get('wa', '')
    if "menunggu" in raw_wa.lower() or raw_wa == "":
        nomor_bersih = "#" # Matikan link jika belum ada izin
    else:
        # Bersihkan nomor jika data asli sudah ada
        nomor_bersih = raw_wa.replace("-", "").replace(" ", "")
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
        rt_alamat=rt_info['alamat'],
        rt_wa_clean=nomor_bersih
    )

# --- 5. RUN SERVER ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
