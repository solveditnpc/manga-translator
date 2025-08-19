import fasttext
import os
import json

input_file = '/data/input.json'
output_file = '/data/output.json'
model_path = '/app/models/lid.176.ftz'

try:
    model = fasttext.load_model(model_path)

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    texts = data.get('rec_texts', [])
    output_data = {
        "detected_languages": []
    }
    
    for text in texts:
        predictions = model.predict(text, k=1)
        language_code = predictions[0][0].replace('__label__', '')
        output_data["detected_languages"].append(language_code)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)

except Exception as e:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"error": str(e)}, f)