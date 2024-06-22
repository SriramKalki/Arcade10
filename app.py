from flask import Flask, render_template, request, redirect, url_for, flash
from transformers import pipeline
from langdetect import detect

app = Flask(__name__)
app.secret_key = 'idk'

# Load pre-trained model
summarizer = pipeline('summarization')

def summarize_text(text, lang='en'):
    if lang != 'en':
        summarizer = pipeline('summarization', model=f'{lang}_summarization_model')
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.form['text']
    if not text:
        flash('No text provided!')
        return redirect(url_for('home'))
    lang = detect(text)
    summary = summarize_text(text, lang)
    return render_template('result.html', summary=summary, original_text=text)

if __name__ == '__main__':
    app.run(debug=True)