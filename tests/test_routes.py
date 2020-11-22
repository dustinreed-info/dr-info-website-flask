from src.app import create_app

flask_app = create_app()

# Create a test client using the Flask application configured for testing
with flask_app.test_client() as test_client:

    def test_routes():
        """
        GIVEN a Flask application configured for testing
        WHEN a route is requested (GET)
        THEN check that the response is valid
        """

        routes = [
            "/",
            "/index",
            "/home",
            "/contact",
            "/about",
            "/certs",
            "/certifications",
            "/Resume",
            "/Resume-Reed-Dustin",
            "/Resume-Reed-Dustin.pdf",
            "/resume",
            "/aws-cda",
            "/aws-cda-cert.pdf",
            "/aws-csa",
            "/aws-csa.cert.pdf",
            "/aws-csa-cert.pdf",
            "/projects",
            "/favicon.ico"
        ]

        for route in routes:
            response = test_client.get(route)
            assert response.status_code == 200

    def test_404():
        """
        GIVEN a Flask application configured for testing
        WHEN an invalid route is requested (GET)
        THEN check that the response is not valid
        """
        errorURL = "gdfipjdfgspi"
        response = test_client.get(errorURL)
        assert response.status_code == 404
