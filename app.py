import os
import json
import boto3
from flask import Flask, request
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

    def load_visitor_count():
        """Load visitor count from S3"""
        if not s3_client:
            return 0

        try:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=VISITOR_COUNT_KEY)
            body = response['Body']
            content = body.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            data = json.loads(content)
            return data.get('count', 0)
        except s3_client.exceptions.NoSuchKey:
            # File doesn't exist yet, start with 0
            return 0
        except Exception as e:
            print(f"Warning: Could not load visitor count from S3: {e}")
            return 0

    def save_visitor_count(count):
        """Save visitor count to S3"""
        if not s3_client:
            return

        try:
            data = {'count': count}
            json_string = json.dumps(data)
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=VISITOR_COUNT_KEY,
                Body=json_string,
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Warning: Could not save visitor count to S3: {e}")

    @application.before_request
    def track_visitors():
        """Track unique visitors (basic IP-based tracking)"""
        if request.endpoint and request.endpoint not in ['static', 'favicon']:
            client_ip = request.remote_addr
            if client_ip:
                current_count = load_visitor_count()
                # For simplicity, just increment on each request
                # In production, you'd want more sophisticated unique visitor tracking
                save_visitor_count(current_count + 1)

    @application.route('/stats')
    def visitor_stats():
        """Hidden endpoint to view visitor statistics"""
        count = load_visitor_count()
        return {
            'visitor_count': count,
            'message': f'Total visitors: {count}',
            'storage': f'S3 ({S3_BUCKET})',
            'status': 'success'
        }

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
