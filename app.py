import os
from flask import Flask
from flask import render_template, flash, redirect, url_for
from flask import send_file, send_from_directory


app = Flask(__name__)


@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html', title="Home")


@app.route('/contact')
def contact():
    return render_template('contact.html', title="Contact")


@app.route('/about')
def about():
    return render_template('about.html', title="About")


@app.route('/certs')
@app.route('/certifications')
def certifications():
    return render_template('certifications.html', title="Certifications")


@app.route('/Resume')
@app.route('/Resume-Reed-Dustin')
@app.route('/Resume-Reed-Dustin.pdf')
@app.route('/resume')
def resume():
    return send_file(
        './static/Resume-Reed-Dustin.pdf',
        attachment_filename="Resume-Reed-Dustin.pdf"
    )


@app.route('/aws-cda')
@app.route('/aws-cda-cert.pdf')
def aws_cda_cert():
    return send_file(
        './static/aws-cda-cert.pdf',
        attachment_filename="aws-cda-cert.pdf"
    )


@app.route('/aws-csa')
# Had  typo in old resume.
@app.route('/aws-csa.cert.pdf')
@app.route('/aws-csa-cert.pdf')
def aws_csa_cert():
    return send_file(
        './static/aws-csa-cert.pdf',
        attachment_filename="aws-csa-cert.pdf"
    )


@app.route('/projects')
def projects():
    return render_template('projects.html', title="Projects")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="Error"), 404


if __name__ == "__main__":
    app.run("0.0.0.0")
