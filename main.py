from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'una_clave_secreta_muy_dificil_de_adivinar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:142857@127.0.0.1:5432/futbol5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    telefono = db.Column(db.String(50))
    password = db.Column(db.String(255))
    alquileres = db.relationship('Alquiler', backref='cliente', lazy=True)


class Cancha(db.Model):
    __tablename__ = 'canchas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    alquileres = db.relationship('Alquiler', backref='cancha', lazy=True)


class Alquiler(db.Model):
    __tablename__ = 'alquileres'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    costo = db.Column(db.Numeric(10, 2), nullable=False)


@app.route('/')
def index():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))

    alquileres = Alquiler.query.all()

    # Calcula la cantidad de alquileres por mes
    month_counts = {}
    for alquiler in alquileres:
        month = alquiler.fecha.month
        month_counts[month] = month_counts.get(month, 0) + 1

    return render_template('index.html', alquileres=alquileres, month_counts=month_counts)

@app.route('/agregar', methods=['POST'])
def agregar():
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form[
            'password']  

        cliente = Cliente.query.filter_by(email=email).first()

        if cliente and cliente.password == password:
            session['cliente_id'] = cliente.id
            return redirect(url_for('index'))

     

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('cliente_id', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)