from flask import Flask, request, jsonify
import os
import json
import keras
import keras_nlp
import tensorflow as tf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)



# Setting up the environment
os.environ["KAGGLE_USERNAME"] = 'kanghyunho'
os.environ["KAGGLE_KEY"] = ''
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

# Load and process the data
template = "Instruction:\n{instruction}\n\nResponse:\n{response}"
data = []
with open("databricks-dolly-15k-ko.jsonl", encoding='utf-8') as file:
    for line in file:
        features = json.loads(line)
        if features["context"]:
            continue
        data.append(template.format(**features))

# Training setup
data = data[:1000]  # Use only 1000 examples for fast processing
gemma_lm = keras_nlp.models.GemmaCausalLM.from_preset("gemma_2b_en")
gemma_lm.backbone.enable_lora(rank=8)
gemma_lm.preprocessor.sequence_length = 512
optimizer = keras.optimizers.AdamW(learning_rate=5e-5, weight_decay=0.01)
optimizer.exclude_from_weight_decay(var_names=["bias", "scale"])
gemma_lm.compile(
    loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    optimizer=optimizer,
    weighted_metrics=[keras.metrics.SparseCategoricalAccuracy()],
)
gemma_lm.fit(data, epochs=3, batch_size=1)

@app.route('/ask', methods=['POST'])
def answer_question():
    content = request.json
    question = content['question']
    prompt = template.format(instruction=question, response="")
    sampler = keras_nlp.samplers.TopKSampler(k=5, seed=2)
    gemma_lm.compile(sampler=sampler)
    response = gemma_lm.generate(prompt, max_length=256)
    response_text = response.split("Response:\n")[-1].strip()
    return jsonify(answer=response_text)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
