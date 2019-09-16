import os
from flask import Flask
from flask import render_template, flash, redirect, url_for
from flask import send_file, send_from_directory


application = Flask(__name__)


@application.route('/')
@application.route('/index')
@application.route('/home')
def index():
    return render_template('index.html', title="Home")


@application.route('/contact')
def contact():
    return render_template('contact.html', title="Contact")


@application.route('/about')
def about():
    return render_template('about.html', title="About")


@application.route('/certs')
@application.route('/certifications')
def certifications():
    return render_template('certifications.html', title="Certifications")


@application.route('/resume')
@application.route('/Resume')
@application.route('/Resume-Reed-Dustin.pdf')
def resume():
    return send_file(
        './static/Resume-Reed-Dustin.pdf',
        attachment_filename="Resume-Reed-Dustin.pdf"
    )


@application.route('/aws-cda')
@application.route('/aws-cda-cert.pdf')
def aws_cda_cert():
    return send_file(
        './static/aws-cda-cert.pdf',
        attachment_filename="aws-cda-cert.pdf"
    )


@application.route('/aws-csa')
@application.route('/aws-csa-cert.pdf')
def aws_csa_cert():
    return send_file(
        './static/aws-csa-cert.pdf',
        attachment_filename="aws-csa-cert.pdf"
    )


@application.route('/projects')
def projects():
    return render_template('projects.html', title="Projects")


@application.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(application.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


if __name__ == "__main__":
    application.run()
