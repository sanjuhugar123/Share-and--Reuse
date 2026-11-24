import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'development-only-secret-key'
    )

    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL:
        # Handle PostgreSQL connection URLs
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace(
                'postgres://',
                'postgresql://',
                1
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:
        # Local development database
        SQLALCHEMY_DATABASE_URI = (
            'sqlite:///' +
            os.path.join(BASE_DIR, 'share_and_reuse.db')
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload configuration
    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(
            BASE_DIR,
            'static',
            'uploads'
        )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Optional Hugging Face compatible image-classification endpoint.
    FOOD_CLASSIFIER_URL = os.environ.get('FOOD_CLASSIFIER_URL')
    FOOD_CLASSIFIER_TOKEN = os.environ.get('FOOD_CLASSIFIER_TOKEN')

    ALLOWED_EXTENSIONS = {
        'png', 'jpg', 'jpeg', 'webp', 'gif'
    }
