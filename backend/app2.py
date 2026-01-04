from flask import Flask, request, jsonify
import tempfile
import asyncio
from uploader import process_file, translate_to_tetum, translate_to_tetum_array
from flask_cors import CORS
from waitress import serve


app = Flask(__name__)

CORS(app)

@app.route('/')
def index():
    return "Hello World!"

"""
This endpoint accepts an Excel or CSV file upload 
and processes it to populate the species_en and species_tet tables in the database.
There is a species.xlsx sample file within the backend folder for testing.
Or you can also run > curl -X POST http://127.0.0.1:5000/upload-species -F "file=@species.xlsx"
"""
@app.route("/upload-species", methods=["POST"])
def upload_species_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        suffix = ".xlsx" if uploaded_file.filename.endswith(".xlsx") else ".csv"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            uploaded_file.save(tmp.name)
            temp_path = tmp.name

        asyncio.run(process_file(temp_path, translate=False))  # English
        asyncio.run(process_file(temp_path, translate=True))   # Tetum

        return jsonify({
            "status": "success",
            "message": "Data uploaded to species_en & species_tet tables"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



async def translateMultipleTexts(texts):
    tasks = [translate_to_tetum(text) for text in texts]
    
    results = await asyncio.gather(*tasks)
    
    return results


@app.route("/translate", methods=["POST"])
def translate():
    print(f"Raw request data: {request.data}")
    data = request.json
    texts = data.get('text', [])
    
    if not texts:
        return {"error": "No text provided"}, 400
    
    
    print(f"Received text: '{texts}'")
    array = asyncio.run(translateMultipleTexts(texts))

    print(f"Translated Text = '{array}")
    
    return jsonify(array)
    

if __name__ == '__main__':
    #app.run(debug=True, port=5000)
    serve(app, host='127.0.0.1', port=5000)