from website import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
    # app.run(host="0.0.0.0", debug=True, ssl_context="adhoc")
