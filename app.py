# Baris 2: Ditambahkan 'session', 'flash'
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Baris 11: [DITAMBAHKAN] Kunci rahasia diperlukan untuk menggunakan 'session'
app.config['SECRET_KEY'] = 'iniadalahkuncirahasia_yang_sangat_aman_dan_acak'
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.route('/')
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

# Baris 30-42: [DITAMBAHKAN] Rute baru untuk login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Ini adalah autentikasi SANGAT SEDERHANA. 
        # Di aplikasi nyata, gunakan HASH PASSWORD!
        if request.form['username'] == 'admin' and request.form['password'] == 'semogabahagia_123':
            session['logged_in'] = True
            flash('Login berhasil!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username atau Password salah.', 'danger')
            return render_template('login.html')
    return render_template('login.html')

# Baris 45-49: [DITAMBAHKAN] Rute baru untuk logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None) # Hapus status login dari session
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_student():
    # Baris 55-57: [DITAMBAHKAN] Pemeriksaan otorisasi/autentikasi
    if not session.get('logged_in'):
        flash('Anda harus login untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('login'))

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    

    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()
    query = "INSERT INTO student (name, age, grade) VALUES (?, ?, ?)"
    cursor.execute(query,(name, age, grade))
    connection.commit()
    connection.close()
    return redirect(url_for('index'))

#Kode awal sebelum diubah
#@app.route('/delete/<string:id>') 
#def delete_student(id):
#    # RAW Query
#    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
#   db.session.commit()
#   return redirect(url_for('index'))

# Baris 88-89: [DIUBAH] Rute '/delete' sekarang HANYA menerima metode POST
@app.route('/delete/<string:id>', methods=['POST']) 
def delete_student(id):
    # Baris 91-93: [DITAMBAHKAN] Pemeriksaan otorisasi/autentikasi
    if not session.get('logged_in'):
        flash('Anda harus login untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('login'))

    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    flash('Data siswa berhasil dihapus.', 'success')
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    # Baris 105-107: [DITAMBAHKAN] Pemeriksaan otorisasi/autentikasi
    if not session.get('logged_in'):
        flash('Anda harus login untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # RAW Query
        db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        db.session.commit()
        flash('Data siswa berhasil diperbarui.', 'success')
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
