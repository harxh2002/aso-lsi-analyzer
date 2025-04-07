from flask import Flask, render_template, request, send_file
import os
import csv
from collections import defaultdict
import re

app = Flask(__name__)

# Helper to clean and tokenize

def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

# Dummy AI suggestion generator
def generate_ai_suggestions(title, subtitle, description, keywords):
    top_kw = sorted(keywords, key=lambda k: -keywords[k]['Overall'])[:3]
    return {
        'title': f"Boost your app with {top_kw[0].title()}!",
        'subtitle': f"Now with {top_kw[1]} features",
        'description': f"Experience {top_kw[2]} and more in our latest version."
    }

# Count keyword occurrences in each section

def count_keywords(lsi_keywords, texts):
    counts = defaultdict(lambda: {'YourApp': 0, 'Competitor1': 0, 'Competitor2': 0, 'Competitor3': 0, 'Overall': 0})
    sources = ['YourApp', 'Competitor1', 'Competitor2', 'Competitor3']

    for idx, text_group in enumerate(texts):
        all_text = ' '.join(text_group).lower()
        for kw in lsi_keywords:
            occurrences = len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b', all_text))
            counts[kw][sources[idx]] += occurrences
            counts[kw]['Overall'] += occurrences

    return counts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        title = request.form['title']
        subtitle = request.form['subtitle']
        description = request.form['description']

        comp1_title = request.form['comp1_title']
        comp1_sub = request.form['comp1_subtitle']
        comp1_desc = request.form['comp1_description']

        comp2_title = request.form['comp2_title']
        comp2_sub = request.form['comp2_subtitle']
        comp2_desc = request.form['comp2_description']

        comp3_title = request.form['comp3_title']
        comp3_sub = request.form['comp3_subtitle']
        comp3_desc = request.form['comp3_description']

        custom_lsi = request.form['custom_lsi'].split(',')
        custom_lsi = [kw.strip() for kw in custom_lsi if kw.strip()]

        # AI Suggestions
        all_keywords = tokenize(title + subtitle + description)
        ai_suggestions = generate_ai_suggestions(title, subtitle, description, defaultdict(lambda: {'Overall': 1}, {kw: {'Overall': 1} for kw in all_keywords}))

        # Count keyword occurrences
        texts = [
            [title, subtitle, description],
            [comp1_title, comp1_sub, comp1_desc],
            [comp2_title, comp2_sub, comp2_desc],
            [comp3_title, comp3_sub, comp3_desc]
        ]
        keyword_occurrences = count_keywords(custom_lsi, texts)

        # LSI by section
        lsi_analysis = {
            'title': [kw for kw in custom_lsi if kw.lower() in tokenize(title)],
            'subtitle': [kw for kw in custom_lsi if kw.lower() in tokenize(subtitle)],
            'description': [kw for kw in custom_lsi if kw.lower() in tokenize(description)]
        }

        # Save CSV
        csv_path = os.path.join('static', 'output.csv')
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Keyword', 'YourApp', 'Competitor1', 'Competitor2', 'Competitor3', 'Overall'])
            for kw, counts in keyword_occurrences.items():
                writer.writerow([kw, counts['YourApp'], counts['Competitor1'], counts['Competitor2'], counts['Competitor3'], counts['Overall']])

        return render_template('result.html', 
                               ai_suggestions=ai_suggestions,
                               keyword_occurrences=keyword_occurrences,
                               lsi_analysis=lsi_analysis)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/download_csv')
def download_csv():
    path = os.path.join('static', 'output.csv')
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
