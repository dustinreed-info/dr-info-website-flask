import os
import json
import boto3
from flask import Flask, request
from flask import render_template, flash, redirect, url_for
from flask import send_file, send_from_directory
from visitor_tracking import tracker
from datetime import datetime, timedelta


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
    @application.route('/Resume-Reed-Dustin.pdf')
    @application.route('/resume')
    @application.route('/Resume-Reed-Dustin')
    def resume():
        return send_from_directory(
            './static',
            'Resume-Reed-Dustin.pdf',
            as_attachment=True
        )


    @application.route('/aws-cda')
    @application.route('/aws-cda-cert.pdf')
    @application.route('/static/aws-cda-cert.pdf')
    def aws_cda_cert():
        return send_from_directory(
            'static',
            'aws-cda-cert.pdf',
            as_attachment=True
        )

    @application.route('/aws-csa')
    # Had typo in old resume.
    @application.route('/aws-csa-cert.pdf')
    @application.route('/static/aws-csa-cert.pdf')
    def aws_csa_cert():
        return send_from_directory(
            'static',
            'aws-csa-cert.pdf',
            as_attachment=True
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


    # Visitor tracking using S3 for multi-instance support
    S3_BUCKET = os.environ.get('S3_BUCKET', 'mail.dustinreed.info')
    VISITOR_COUNT_KEY = 'visitor_count.json'

    # Initialize S3 client
    try:
        s3_client = boto3.client('s3')
    except Exception as e:
        print(f"Warning: Could not initialize S3 client: {e}")
        s3_client = None

    def get_real_client_ip(request):
        """Get the real client IP address, accounting for proxies"""
        # Check for X-Forwarded-For header (most common with proxies/load balancers)
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first (original client)
            client_ip = x_forwarded_for.split(',')[0].strip()
            return client_ip

        # Check for X-Real-IP header (nginx)
        x_real_ip = request.headers.get('X-Real-IP')
        if x_real_ip:
            return x_real_ip.strip()

        # Check for CF-Connecting-IP header (Cloudflare)
        cf_connecting_ip = request.headers.get('CF-Connecting-IP')
        if cf_connecting_ip:
            return cf_connecting_ip.strip()

        # Fall back to remote_addr
        return request.remote_addr

    @application.before_request
    def track_visitors():
        """Track unique visitors with IP-based counting and user agent analysis"""
        if request.endpoint and request.endpoint not in ['static', 'favicon']:
            # Get real client IP, accounting for proxies
            client_ip = get_real_client_ip(request)
            user_agent = request.headers.get('User-Agent')
            tracker.track_visitor(client_ip, user_agent)

    @application.route('/analytics')
    @application.route('/stats')
    def analytics():
        """Display visitor analytics dashboard"""
        stats = tracker.get_stats_for_template()
        return render_template('analytics.html', title="Analytics", **stats)

    @application.route('/api/stats')
    def visitor_stats():
        """JSON API endpoint for visitor statistics"""
        return tracker.get_stats_for_api()

    @application.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', title="Error"), 404

    return application


application = create_app()

if __name__ == "__main__":
    # Only enable debug mode when running locally/development
    debug_mode = (
        os.environ.get('FLASK_ENV') == 'development' or 
        os.environ.get('FLASK_DEBUG') == '1' or
        not os.environ.get('FLASK_ENV')  # Default to debug if no environment set
    )
    application.run("0.0.0.0", debug=debug_mode)
