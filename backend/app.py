from flask import Flask, request, jsonify
from flask_cors import CORS
from projectplanning import (
    create_project_plan,
    create_backlog,
    create_sprint_plan,
    update_progress,
)
from integrations import jira, asana

app = Flask(__name__)
CORS(app)

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    try:
        data = request.json
        result = create_project_plan(data)
        
        if result.get('success', False):
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 400
            
    except Exception as e:
        print(f"Error in generate_plan: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/create-backlog', methods=['POST'])
def api_create_backlog():
    data = request.json
    backlog = create_backlog(data)
    return jsonify({'backlog': backlog})


@app.route('/plan-sprint', methods=['POST'])
def api_plan_sprint():
    data = request.json
    sprint = create_sprint_plan(data)
    return jsonify({'sprint': sprint})


@app.route('/progress-update', methods=['POST'])
def api_progress_update():
    data = request.json
    progress = update_progress(data)
    return jsonify({'progress': progress})


@app.route('/sync-external', methods=['POST'])
def sync_external():
    data = request.json
    title = data.get('title', 'Untitled')
    description = data.get('description', '')
    jira.create_issue(title, description)
    asana.create_task(title, description)
    return jsonify({'synced': True})

if __name__ == '__main__':
    app.run(debug=True)
