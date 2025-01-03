from flask import Flask, request, jsonify
from flask_cors import CORS
from projectplanning import create_project_plan

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

if __name__ == '__main__':
    app.run(debug=True)
