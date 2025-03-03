import os
from app import app

# Basic error handling
@app.errorhandler(500)
def handle_500_error(e):
    return {"error": "Internal Server Error"}, 500

@app.errorhandler(404)
def handle_404_error(e):
    return {"error": "Not Found"}, 404

if __name__ == '__main__':
    app.run()
