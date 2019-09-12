import os
from flask import Flask
from flask import render_template, flash, redirect, url_for


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")


application = Flask(__name__)
application.config.from_object(Config)


@application.route('/')
@application.route('/index')
@application.route('/home')
def index():
    return render_template('index.html', title='Home')
@application.route('/contact')
def contact():
    return render_template('contact.html')
@application.route('/about')
def about():
    return render_template('about.html')
@application.route('/certifications')
def certifications():
    return render_template('certifications.html')
@application.route('/resume')
def resume():
    return url_for('static', filename='Resume-Reed-Dustin.pdf')
@application.route('/projects')
def projects():
    return render_template('projects.html')




if __name__ == "__main__":
    application.run()