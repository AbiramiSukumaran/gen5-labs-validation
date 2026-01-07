# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from db_manager import DBManager
from ai_manager import AIManager
from config import Config
import base64
import pandas as pd
import io

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Managers
db = DBManager()
ai = AIManager()

# Helpers
def is_owner():
    return session.get('role') == 'OWNER'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = db.check_credentials(username, password)
        
        if role:
            session['username'] = username
            session['role'] = role
            session['password'] = password 
            if role == 'OWNER':
                return redirect(url_for('owner_dashboard'))
            else:
                return redirect(url_for('developer_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- OWNER ROUTES ---
@app.route('/owner', methods=['GET'])
def owner_dashboard():
    if not is_owner(): return redirect(url_for('login'))
    return render_template('owner_dashboard.html')

@app.route('/owner/add_session', methods=['POST'])
def add_session():
    if not is_owner(): return redirect(url_for('login'))
    try:
        # File handling for sample screenshot
        f = request.files['sample_screenshot']
        img_b64 = base64.b64encode(f.read()).decode('utf-8') if f else None
        
        success, msg = db.create_season_session(
            int(request.form['season_number']),
            request.form['start_date'],
            request.form['end_date'],
            request.form['sub_end_date'],
            int(request.form['session_number']),
            request.form['session_title'],
            request.form['link'],
            int(request.form['step']),
            request.form['description'],
            img_b64
        )
        if success: flash('Session added successfully!', 'success')
        else: flash(f'Error: {msg}', 'error')
    except Exception as e:
        flash(f'System Error: {str(e)}', 'error')
        
    return redirect(url_for('owner_dashboard'))

@app.route('/owner/generate_creds', methods=['POST'])
def generate_creds():
    if not is_owner(): return redirect(url_for('login'))
    try:
        count = int(request.form['count'])
        MAX_LIMIT = 50000 
        
        if count > MAX_LIMIT:
            flash(f'Cannot generate more than {MAX_LIMIT} credentials at once.', 'error')
            return redirect(url_for('owner_dashboard'))
        
        creds = db.generate_bulk_credentials(count)
        df = pd.DataFrame(creds)
        output = io.StringIO()
        df.to_csv(output, index=False)
        return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=credentials.csv"})
    except Exception as e:
        flash(f'Error generating credentials: {str(e)}', 'error')
        return redirect(url_for('owner_dashboard'))

@app.route('/owner/leaderboard')
def leaderboard():
    if not is_owner(): return redirect(url_for('login'))
    data = db.get_leaderboard()
    return render_template('leaderboard.html', data=data)

# --- DEVELOPER ROUTES ---
@app.route('/developer', methods=['GET'])
def developer_dashboard():
    if session.get('role') != 'DEVELOPER': return redirect(url_for('login'))
    
    season_num = db.get_active_season()
    sessions = []
    if season_num:
        sessions = db.get_sessions_for_season(season_num)

    stats = db.get_developer_stats(session['username'])
    return render_template('developer_dashboard.html', season=season_num, sessions=sessions, stats=stats)

@app.route('/developer/submit', methods=['POST'])
def submit_result():
    if session.get('role') != 'DEVELOPER': return redirect(url_for('login'))
    
    season = int(request.form['season'])
    session_id = int(request.form['session'])
    desc = request.form['description_hidden'] 
    file = request.files['screenshot']
    force_submit = request.form.get('force_submit') == 'on'
    
    # Get retry count from the hidden field populated by JS
    try:
        retry_count = int(request.form.get('retry_count_hidden', 1))
    except:
        retry_count = 1

    current_status = db.get_developer_status(session['username'], season, session_id)
    if current_status:
        flash('You have already submitted a result for this session. No further updates allowed.', 'warning')
        return redirect(url_for('developer_dashboard'))

    img_bytes = file.read()
    approved, comment = ai.validate_submission(img_bytes, desc)
    
    if approved:
        db.submit_attempt(session['username'], session['password'], season, session_id, 'APPROVED', comment, retry_count, intervention=False)
        flash(f'Success! {comment}', 'success')

    elif not approved and force_submit:
        db.submit_attempt(session['username'], session['password'], season, session_id, 'REJECTED', comment, retry_count, intervention=True)
        flash('Submission recorded for manual intervention. This cannot be changed.', 'warning')

    else:
        flash(f'Validation Failed: {comment}', 'error')
        flash('Action Required: Retry with a correct screenshot.', 'warning')
            
    return redirect(url_for('developer_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)