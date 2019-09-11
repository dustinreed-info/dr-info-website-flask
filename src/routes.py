from flask import render_template, flash, redirect, url_for
from src import app

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html', title='Home')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/certifications')
def certifications():
    return render_template('certifications.html')
@app.route('/resume')
def resume():
    return url_for('static', filename='Resume-Reed-Dustin.pdf')
@app.route('/projects')
def projects():
    return render_template('projects.html')