from flask import Flask, render_template, request, redirect, url_for, flash
from transformers import pipeline

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Load pre-trained model
summarizer = pipeline('summarization')

def summarize_text(text):
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
    summary = summarize_text(text)
    return render_template('result.html', summary=summary, original_text=text)

if __name__ == '__main__':
    app.run(debug=True)