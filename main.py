from website import create_app

if __name__ == "__main__":
    app = create_app()
    # app.run(threaded=True)
    # app.run(debug=True, threaded=True)
    # app.run(host="127.0.0py.1", debug=True, threaded=True)
    app.run(host="0.0.0.0", debug=True, threaded=True)
    # app.run(host="0.0.0.0", debug=True, ssl_context="adhoc")
