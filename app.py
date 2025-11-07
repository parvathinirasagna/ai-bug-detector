from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from bug_detector import BugDetector
from ml_models import MLBugDetector

app = Flask(__name__)
CORS(app)

bug_detector = BugDetector()
ml_detector = MLBugDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code.strip():
            return jsonify({'error': 'No code provided'}), 400
        
        # Rule-based detection
        results = bug_detector.analyze_code(code, language)
        
        # ML-based detection
        if data.get('use_ml', True):
            ml_results = ml_detector.analyze_with_ml(code)
            results['ml_insights'] = ml_results.get('ml_insights', [])
            results['confidence_score'] = ml_results.get('confidence_score', 0.0)
        
        # Statistics
        total_issues = (
            len(results.get('syntax_errors', [])) +
            len(results.get('logical_bugs', [])) +
            len(results.get('antipatterns', []))
        )
        
        results['total_issues'] = total_issues
        results['lines_analyzed'] = len(code.split('\n'))
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

if __name__ == '__main__':
    print("🚀 Starting AI Bug Detection System...")
    print("📊 Based on research: GRU+CNN, NLP, and ML techniques")
    print("🌐 Open: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
