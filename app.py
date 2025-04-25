import os
import sys
from src import create_app, db
from seed_data import seed_database

# Ensure the instance directory is writable
instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
os.makedirs(instance_dir, exist_ok=True)
try:
    # Try to write a test file to check permissions
    test_file = os.path.join(instance_dir, 'test_file')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
except PermissionError:
    print("ERROR: No write permission in the instance directory!")
    print(f"Please run: chmod -R 777 {instance_dir}")
    sys.exit(1)

app = create_app()

# Seed the database if environment variable is set
if os.environ.get('SEED_DATABASE'):
    with app.app_context():
        print("Seeding database on startup...")
        # Make sure tables are created
        db.create_all()
        # Seed the database
        seed_result = seed_database()
        if seed_result:
            print("Database seeded successfully!")
        else:
            print("WARNING: Database seeding failed.")

if __name__ == '__main__':
    # Use the port from environment variable if set, otherwise use 8080 
    # (to avoid macOS AirPlay Receiver conflict on port 5000)
    port = int(os.environ.get('FLASK_RUN_PORT', 8080))
    app.run(debug=True, port=port)