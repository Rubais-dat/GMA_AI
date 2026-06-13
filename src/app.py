import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

# Load .env file
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
# Enable CORS for frontend flexibility
CORS(app)

# Import our hybrid query engine from query_llm
from query_llm import query

@app.route('/query', methods=['POST'])
def query_api():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "No 'question' field provided in the request."}), 400
        
    question = data.get('question')
    history = data.get('history', [])
    
    try:
        # Run hybrid retrieval and LLM generation with conversational history
        answer, sources = query(question, history=history)
        return jsonify({
            "answer": answer,
            "sources": sources
        })
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Run the API server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Flask server on port {port}...")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
