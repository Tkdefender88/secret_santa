"""Flask web application for secret santa."""

from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from db import init_db, add_person, get_all_people, clear_people, save_assignments, get_assignment, get_all_assignments
from santa import SantaAssigner
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

@app.before_request
def log_request_info():
    print(f"Request: {request.method} {request.path}")


# Admin password - set via environment or default to 'admin'
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')


def require_admin_auth(f):
    """Decorator to require admin authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_admin_password(auth.password):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


def check_admin_password(password):
    """Check if password is correct."""
    return password == ADMIN_PASSWORD


def format_people_for_assigner(people):
    """Convert DB people format to SantaAssigner format."""
    return [
        {'id': str(p['id']), 'name': p['name'], 'surname': p['surname']}
        for p in people
    ]


def assignments_to_int_keys(assignments):
    """Convert string keys to int keys for database."""
    return {int(k): int(v) for k, v in assignments.items()}


@app.route('/')
def index():
    """Home page - show name tiles for users to pick."""
    picked_id = request.cookies.get('picked_person_id')
    people = get_all_people()
    has_assignments = len(get_all_assignments()) > 0
    return render_template('index.html', people=people, has_assignments=has_assignments, picked_id=picked_id)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if check_admin_password(password):
            response = make_response(redirect('/admin'))
            response.set_cookie('admin_auth', 'true', httponly=True, secure=True, samesite='Strict')
            return response
        return render_template('admin_login.html', error='Invalid password')
    return render_template('admin_login.html')


def require_admin_cookie(f):
    """Decorator to check admin auth cookie."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.cookies.get('admin_auth') != 'true':
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin')
@require_admin_cookie
def admin():
    """Admin page - manage participants and draw."""
    people = get_all_people()
    has_assignments = len(get_all_assignments()) > 0
    return render_template('admin_manage.html', people=people, has_assignments=has_assignments)


@app.route('/admin/logout')
def admin_logout():
    """Logout admin."""
    response = make_response(redirect('/'))
    response.delete_cookie('admin_auth')
    return response


@app.route('/api/people', methods=['GET'])
def list_people():
    """Get all people."""
    people = get_all_people()
    return jsonify(people)


@app.route('/api/people', methods=['POST'])
def create_person():
    """Add a new person."""
    data = request.json
    name = data.get('name', '').strip()
    surname = data.get('surname', '').strip()
    
    if not name or not surname:
        return jsonify({'error': 'Name and surname required'}), 400
    
    person_id = add_person(name, surname)
    return jsonify({'id': person_id, 'name': name, 'surname': surname}), 201


@app.route('/api/people', methods=['DELETE'])
def clear_all_people():
    """Delete all people."""
    clear_people()
    return jsonify({'status': 'cleared'}), 200


@app.route('/api/draw', methods=['POST'])
def draw():
    """Perform the secret santa drawing."""
    people = get_all_people()
    
    if len(people) < 2:
        return jsonify({'error': 'Need at least 2 people'}), 400
    
    formatted_people = format_people_for_assigner(people)
    assigner = SantaAssigner(formatted_people)
    
    if not assigner.assign():
        return jsonify({'error': 'No valid assignment possible. Check for invalid group configuration.'}), 400
    
    # Convert assignments to int keys and save
    assignments_int = assignments_to_int_keys(assigner.get_assignments())
    save_assignments(assignments_int)
    
    return jsonify({'status': 'drawn', 'count': len(people)}), 200


@app.route('/api/assignment/<int:person_id>')
def get_my_assignment(person_id):
    """Get who a person needs to buy a gift for."""
    assignment = get_assignment(person_id)
    
    if not assignment:
        return jsonify({'error': 'No assignment found'}), 404
    
    return jsonify(assignment), 200


@app.route('/admin/assignments')
@require_admin_cookie
def admin_view():
    """Admin view of all assignments."""
    people = get_all_people()
    assignments = get_all_assignments()
    
    assignment_list = []
    for person in people:
        recipient_id = assignments.get(person['id'])
        if recipient_id:
            recipient = next((p for p in people if p['id'] == recipient_id), None)
            assignment_list.append({
                'giver': f"{person['name']} {person['surname']}",
                'recipient': f"{recipient['name']} {recipient['surname']}" if recipient else 'Unknown'
            })
    
    return render_template('admin.html', assignments=assignment_list)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
