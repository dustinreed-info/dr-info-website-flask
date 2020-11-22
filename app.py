import os
from flask import Flask
from flask import render_template, flash, redirect, url_for
from flask import send_file, send_from_directory


def create_app(config_filename=None):
    application = Flask(__name__)
    if config_filename is not None:
        application.config.from_pyfile(config_filename)

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


    @application.route('/Resume')
    @application.route('/Resume-Reed-Dustin')
    @application.route('/Resume-Reed-Dustin.pdf')
    @application.route('/resume')
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
    # Had  typo in old resume.
    @application.route('/aws-csa.cert.pdf')
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


    @application.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', title="Error"), 404

    return application


application = create_app()

if __name__ == "__main__":
    application.run("0.0.0.0")
