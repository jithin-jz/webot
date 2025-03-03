# Instagram Bot Web Application

A professional web application for managing Instagram automation tasks with a beautiful Instagram-style UI.

## Features

- Instagram-style UI with dark mode support
- Real-time task status updates
- Background task processing
- Rate limiting and API safety measures
- Session management
- Production-ready configuration
- Security headers and best practices

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd instagram-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development Setup

1. Set environment variables:
```bash
export FLASK_APP=wsgi.py
export FLASK_ENV=development
```

2. Run the development server:
```bash
flask run
```

## Production Deployment

1. Set environment variables:
```bash
export FLASK_APP=wsgi.py
export FLASK_ENV=production
export SECRET_KEY=<your-secret-key>
export REDIS_URL=<your-redis-url>  # Optional, for session storage
```

2. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t instagram-bot .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 \
  -e SECRET_KEY=<your-secret-key> \
  -e REDIS_URL=<your-redis-url> \
  instagram-bot
```

## Security Considerations

- All Instagram credentials are handled securely and never stored
- Rate limiting is implemented to prevent API abuse
- Security headers are configured for production
- Session management uses secure cookies
- CSRF protection is enabled
- Content Security Policy is configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
