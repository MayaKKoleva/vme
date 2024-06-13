from flask import Blueprint, render_template, request, flash, jsonify, redirect, send_from_directory, current_app, url_for
from flask_login import login_required, current_user
from .models import Note, File
from . import db
import json
import os

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')
        date = request.form.get('date')
        time = request.form.get('time')
        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, date=date, time=time, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Task added!', category='success')

    files = File.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", user=current_user, files=files)

@views.route('/uploads', methods=['POST'])
@login_required
def uploads():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            new_file = File(filename=filename, user_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()
            flash('File uploaded successfully!', category='success')
            return redirect('/board')
    flash('File upload failed!', category='error')
    return redirect('/board')

@views.route('/uploaded_file/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@views.route('/download/<int:file_id>')
@login_required
def download(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('You do not have permission to download this file!', category='error')
        return redirect('/board')
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True)

@views.route('/delete/<int:file_id>')
@login_required
def delete(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('You do not have permission to delete this file!', category='error')
        return redirect('/board')
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        db.session.delete(file)
        db.session.commit()
        flash('File deleted successfully!', category='success')
    else:
        flash('File not found!', category='error')
    return redirect('/board')

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():  
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
    return jsonify({})

@views.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@views.route('/list')
@login_required
def list():
    return render_template("list.html", user=current_user)

@views.route('/board')
@login_required
def board():
    files = File.query.filter_by(user_id=current_user.id).all()
    return render_template("board.html", user=current_user, files=files)
