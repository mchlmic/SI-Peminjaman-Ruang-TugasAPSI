from flask import render_template, request, flash, redirect, url_for, session, send_file, current_app
from werkzeug.security import check_password_hash
from app import app, mysql
from base64 import b64decode
import os

# rute homepage
@app.route('/')
def index():
    if 'loggedin' in session:
        # Periksa apakah pengguna adalah sekretaris dan sudah diverifikasi
        if session.get('level') == 'Sekretaris' and not session.get('sekretaris_verified'):
            flash('Harap verifikasi sebagai sekretaris terlebih dahulu', 'danger')
            return redirect(url_for('verifikasi_sekretaris'))
        return render_template('index.html')
    return redirect(url_for('login'))


# rute registrasi
@app.route('/registrasi', methods=('GET','POST'))
def registrasi():
    if request.method == 'POST':
        username = request.form['username']
        nim = request.form['nim']
        email = request.form['email']
        level = request.form['level']

        #cek username atau nim
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM tb_users WHERE username=%s OR nim=%s',(username, nim, ))
        akun = cursor.fetchone()
        if akun is None:
            cursor.execute('INSERT INTO tb_users VALUES (NULL, %s, %s, %s, %s)', (username, nim, email, level))
            mysql.connection.commit()
            flash('Registrasi Berhasil','success')
        else :
            flash('Username atau nim sudah ada','danger')
    return render_template('registrasi.html')

# rute login
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        nim = request.form['nim']

        # cek data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM tb_users WHERE username=%s', (username,))
        akun = cursor.fetchone()

        if akun is None:
            flash('Login Gagal, Cek Username Anda', 'danger')
        else:
            # Cetak akun untuk debugging
            print("Data akun:", akun)

            # Ganti kondisi ini dengan menggunakan nama kolom yang sesuai
            if 'nim' in akun and akun['nim'] != nim:
                flash('Login Gagal, Cek NIM Anda', 'danger')
            else:
                session['loggedin'] = True
                session['username'] = akun['username']
                
                # Sesuaikan dengan kolom yang sesuai
                session['level'] = akun['level']

                # Simpan nim ke dalam sesi
                session['nim'] = nim

                return redirect(url_for('index'))

    return render_template('login.html')

# rute logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('level', None)
    session.pop('sekretaris_verified', None)
    
    return redirect(url_for('login'))

# rute verifikasi sekretaris
@app.route('/verifikasi_sekretaris', methods=['GET', 'POST'])
def verifikasi_sekretaris():
    if request.method == 'POST':
        kode_password = request.form['kode_password_sekretaris']

        # logika untuk kode verifikasi password sekretaris
        if kode_password == 'KodeSekre123':
            # Jika verifikasi berhasil, set flag di sesi untuk menandakan bahwa sekretaris telah diverifikasi
            session['sekretaris_verified'] = True
            return redirect(url_for('index'))
        else:
            flash('Kode verifikasi salah', 'danger')

    return render_template('verifikasi_sekretaris.html')

# rute status
@app.route('/status')
def status():
    # Memastikan hanya pengguna yang telah login yang dapat mengakses halaman ini
    if 'loggedin' not in session:
        flash('Anda harus login untuk mengakses halaman', 'danger')
        return redirect(url_for('login'))

    # Mendapatkan data buatsurat dari database berdasarkan nim pengguna yang saat ini login
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_buatsurat WHERE nim = %s", (session['nim'],))
    buatsurat_data = cur.fetchall()
    cur.close()

    # Mendapatkan data tandatangan dari database berdasarkan nim pengguna yang saat ini login
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_tandatangan WHERE nim = %s", (session['nim'],))
    tandatangan_data = cur.fetchall()
    cur.close()

    return render_template('status.html', buatsurat_data=buatsurat_data, tandatangan_data=tandatangan_data)

# rute status sekretaris
@app.route('/statussekre')
def statussekre():
    # Memastikan hanya sekretaris yang dapat mengakses halaman ini
    # Kondisi session['role'] == 'sekretaris'
    if 'loggedin' not in session or session.get('level') != 'Sekretaris':
        flash('Anda tidak diizinkan mengakses halaman ini', 'danger')
        return redirect(url_for('login'))

    # Mendapatkan data buatsurat dari database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_buatsurat")
    buatsurat_data = cur.fetchall()
    cur.close()

    # Mendapatkan data tandatangan dari database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_tandatangan")
    tandatangan_data = cur.fetchall()
    cur.close()
    return render_template('statussekre.html', buatsurat_data=buatsurat_data, tandatangan_data=tandatangan_data)

# rute contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

# rute buat surat
@app.route('/buatsurat', methods=['GET', 'POST'])
def buatsurat():
    if request.method == 'POST':
        # Medapatkan data dari inputan form
        nama = request.form['username']
        nim = request.form['nim']
        email = request.form['email']
        jenis_surat = request.form.getlist('jenis_surat[]')
        deskripsi = request.form['deskripsi']

        # Perintah SQL untuk menyimpan data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tb_buatsurat (nama, nim, email, jenis_surat, deskripsi) VALUES (%s, %s, %s, %s, %s)", (nama, nim, email, ', '.join(jenis_surat), deskripsi))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('status'))

    return render_template('buatsurat.html')
import base64

# rute tanda tangan
@app.route('/tandatangan', methods=['GET', 'POST'])
def tandatangan():
    if request.method == 'POST':
        nama = request.form['username']
        nim = request.form['nim']
        email = request.form['email']
        jenis_dokumen = request.form['jenis_dokumen']

        file = request.files['file']
        if file:
            # Simpan file di sistem file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Encode file data ke dalam format base64
            file_data_base64 = base64.b64encode(file.read()).decode('utf-8', 'strict')

            # Eksekusi perintah SQL untuk menyimpan data
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tb_tandatangan (nama, nim, email, jenis_dokumen, file_data) VALUES (%s, %s, %s, %s, %s)",
                        (nama, nim, email, jenis_dokumen, file_data_base64))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('status'))

    return render_template('tandatangan.html')

# rute unduh file
@app.route('/unduh_file/<int:file_id>')
def unduh_file(file_id):
    # Mendapatkan data file dari database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_tandatangan WHERE id = %s", (file_id,))
    file_data = cur.fetchone()
    cur.close()

    if file_data is None:
        return "File not found", 404

    if len(file_data['file_data']) % 4 != 0:
        padding = b'=' * (4 - len(file_data['file_data']) % 4)
        file_data['file_data'] += padding

    file_data_binary = b64decode(file_data['file_data'])

    # Konstruksi path ke file sementara
    temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'unduh_{file_id}.pdf')

    # Simpan file sementara
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_data_binary)

    # Pastikan file ada
    if not os.path.exists(temp_file_path):
        return "File not found", 404

    # Kirim file untuk diunduh
    return send_file(temp_file_path, as_attachment=True)


# rute unggah surat balasan
@app.route('/unggah_surat_balasan/<tabel>/<int:id>', methods=['POST'])
def unggah_surat_balasan(tabel, id):
    print(f"Rute diakses: /unggah_surat_balasan/{tabel}/{id}")
    # Logika pengunggahan surat balasan untuk tabel yang sesuai
    if tabel == 'buatsurat':
        # Logika untuk tb_buatsurat
        if 'surat_balasan' in request.files:
            surat_balasan = request.files['surat_balasan']
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE tb_buatsurat SET surat_balasan='Sudah Diunggah' WHERE id=%s", (id,))
            mysql.connection.commit()
            cursor.close()
        else:
            flash('Gagal mengunggah surat balasan', 'danger')

    elif tabel == 'tandatangan':
        #  Logika untuk tb_tandatangan
        if 'surat_balasan' in request.files:
            surat_balasan = request.files['surat_balasan']
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE tb_tandatangan SET surat_balasan='Sudah Diunggah' WHERE id=%s", (id,))
            mysql.connection.commit()
            cursor.close()
        else:
            flash('Gagal mengunggah surat balasan', 'danger')
    else:
        flash('Tabel tidak dikenali', 'danger')

    return redirect(url_for('statussekre'))

if __name__ == '__main__':
    app.run(debug=True)