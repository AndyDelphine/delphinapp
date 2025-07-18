from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import Select
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from datetime import datetime



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:kGFBerAWzKTWpifaDyCElSEtfAcxNVji@mainline.proxy.rlwy.net:57087/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) 
app.secret_key = "your_secret_key"
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
class FormEntry(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    gender=db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    phonenumber=db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    bloodgroup = db.Column(db.String(10), nullable=False)
    genotype= db.Column(db.String(10), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    anyillness = db.Column(db.String(120))
    lastdonation = db.Column(db.String(20))
    medications = db.Column(db.String(10), nullable=False)   
    notes = db.Column(db.Text) 

with app.app_context():
    db.create_all()


@app.route('/')
def main():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        email_check = db.select(User).where(User.email == email)
        user = db.session.execute(email_check).scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            form_entry = FormEntry.query.filter_by(email=email).first()

            if form_entry:
                return redirect(url_for('donorsearch', user_id=form_entry.id))
            else:
                return redirect(url_for('form'))
        else:
            flash("Invalid email or password", category='danger')
    return render_template('login.html')

@app.route('/register',methods=[ 'GET', 'POST'])
def register():
    if request.method == 'POST':
       name= request.form.get('username')
       email= request.form.get('email')
       password= request.form.get('password')
       hashed_password= generate_password_hash(password)
       new_user = User(username =  name, email=email, password = hashed_password)
       db.session.add(new_user)
       db.session.commit()
       login_user(new_user)
       return redirect(url_for('form'))       
    return render_template('register.html')


@app.route('/form',methods=[ 'GET', 'POST'])
@login_required
def form():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        gender= request.form.get('gender')
        dob = request.form.get('dob')
        phonenumber = request.form.get('phonenumber')
        email = request.form.get('email')
        address = request.form.get('address') 
        bloodgroup = request.form.get('bloodgroup')
        genotype = request.form.get('genotype')
        weight = int(request.form.get('weight'))
        anyillness = ', '.join(request.form.getlist('anyillness'))
        lastdonation= request.form.get('lastdonation')
        medications = request.form.get('medications')
        notes = request.form.get('notes')

        donor = FormEntry(
            fullname = fullname,
            gender = gender,
            dob = dob,
            phonenumber = phonenumber,
            email = email,
            address = address,
            bloodgroup = bloodgroup,
            genotype = genotype,
            weight = weight,
            anyillness = anyillness,
            lastdonation = lastdonation,
            medications = medications,
            notes = notes
        )
            
        db.session.add(donor)
        db.session.commit()
        return redirect(url_for('donorsearch',user_id=donor.id))
    
    return render_template('form.html')

@app.route('/donorsearch/<int:user_id>',methods=[ 'GET'])
def donorsearch(user_id):
    form_user =FormEntry.query.get_or_404(user_id)

    search_group = request.args.get('bloodgroup')
    if search_group:
        donors = FormEntry.query.filter(
            FormEntry.bloodgroup == search_group,
            FormEntry.id != form_user.id
        ).all()
    else:
        donors = FormEntry.query.filter(
            FormEntry.id !=form_user.id
        ).all()

        
    return render_template('donorsearch.html', 
        current_user=form_user,
        donors=donors,
        search_group=search_group)

    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)