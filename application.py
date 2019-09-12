import os
from flask import Flask
from flask import render_template, flash, redirect, url_for, send_file


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")


application = Flask(__name__)
application.config.from_object(Config)


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
@application.route('/certifications')
@application.route('/certs')
def certifications():
    return render_template('certifications.html', title="Certifications")
@application.route('/resume')
@application.route('/Resume')
@application.route('/Resume-Reed-Dustin.pdf')
def resume():
    return send_file('./static/Resume-Reed-Dustin.pdf', attachment_filename="Resume-Reed-Dustin.pdf")
@application.route('/projects')
def projects():
    return render_template('projects.html', title="Projects")




if __name__ == "__main__":
    application.run()