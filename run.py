from app import create_app, db

from app.models import User
from app.models import Transaction

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all tables defined in models
    app.run(debug=True)
