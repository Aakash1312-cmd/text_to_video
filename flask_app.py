from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

# --------------------------
# Load Environment Variables
# --------------------------
load_dotenv()
SKETCHFAB_API_TOKEN = os.getenv("SKETCHFAB_API_TOKEN")  # store token in .env file

app = Flask(__name__)

# --------------------------
# Database (Chapter -> Topic -> iframe)
# --------------------------
database = {
    "Reproduction": {
        "Fertilization": """<iframe id="embedded-human" frameBorder="0" style="aspect-ratio: 4 / 3; width: 100%" allowFullScreen="true" loading="lazy" src="https://human.biodigital.com/viewer/?id=6Vaz&ui-anatomy-descriptions=true&ui-anatomy-pronunciations=true&ui-anatomy-labels=true&ui-audio=true&ui-chapter-list=false&ui-fullscreen=true&ui-help=true&ui-info=true&ui-label-list=true&ui-layers=true&ui-skin-layers=true&ui-loader=circle&ui-media-controls=full&ui-menu=true&ui-nav=true&ui-search=true&ui-tools=true&ui-tutorial=false&ui-undo=true&ui-whiteboard=true&initial.none=true&disable-scroll=false&uaid=MGiiL&paid=o_28299092"></iframe>""",
        "Uterus": """<iframe id="embedded-human" frameBorder="0" style="aspect-ratio: 4 / 3; width: 100%" allowFullScreen="true" loading="lazy" src="https://human.biodigital.com/viewer/?id=6Vb0&ui-anatomy-descriptions=true&ui-anatomy-pronunciations=true&ui-anatomy-labels=true&ui-audio=true&ui-chapter-list=false&ui-fullscreen=true&ui-help=true&ui-info=true&ui-label-list=true&ui-layers=true&ui-skin-layers=true&ui-loader=circle&ui-media-controls=full&ui-menu=true&ui-nav=true&ui-search=true&ui-tools=true&ui-tutorial=false&ui-undo=true&ui-whiteboard=true&initial.none=true&disable-scroll=false&uaid=MGiiZ&paid=o_28299092"></iframe>""",
        "In Vitro Fertilization": """<iframe id="embedded-human" frameBorder="0" style="aspect-ratio: 4 / 3; width: 100%" allowFullScreen="true" loading="lazy" src="https://human.biodigital.com/viewer/?id=6Vb1&ui-anatomy-descriptions=true&ui-anatomy-pronunciations=true&ui-anatomy-labels=true&ui-audio=true&ui-chapter-list=false&ui-fullscreen=true&ui-help=true&ui-info=true&ui-label-list=true&ui-layers=true&ui-skin-layers=true&ui-loader=circle&ui-media-controls=full&ui-menu=true&ui-nav=true&ui-search=true&ui-tools=true&ui-tutorial=false&ui-undo=true&ui-whiteboard=true&initial.none=true&disable-scroll=false&uaid=MGiix&paid=o_28299092"></iframe>"""
    },
    "Digestive System": {
        "Stomach": """<iframe id="embedded-human" frameBorder="0" style="aspect-ratio: 4 / 3; width: 100%" allowFullScreen="true" loading="lazy" src="https://human.biodigital.com/viewer/?id=6Vb3&ui-anatomy-descriptions=true&ui-anatomy-pronunciations=true&ui-anatomy-labels=true&ui-audio=true&ui-chapter-list=false&ui-fullscreen=true&ui-help=true&ui-info=true&ui-label-list=true&ui-layers=true&ui-skin-layers=true&ui-loader=circle&ui-media-controls=full&ui-menu=true&ui-nav=true&ui-search=true&ui-tools=true&ui-tutorial=false&ui-undo=true&ui-whiteboard=true&initial.none=true&disable-scroll=false&uaid=MGijD&paid=o_28299092"></iframe>""",
        "Large Intestine": """<iframe id="embedded-human" frameBorder="0" style="aspect-ratio: 4 / 3; width: 100%" allowFullScreen="true" loading="lazy" src="https://human.biodigital.com/viewer/?id=6Vb4&ui-anatomy-descriptions=true&ui-anatomy-pronunciations=true&ui-anatomy-labels=true&ui-audio=true&ui-chapter-list=false&ui-fullscreen=true&ui-help=true&ui-info=true&ui-label-list=true&ui-layers=true&ui-skin-layers=true&ui-loader=circle&ui-media-controls=full&ui-menu=true&ui-nav=true&ui-search=true&ui-tools=true&ui-tutorial=false&ui-undo=true&ui-whiteboard=true&initial.none=true&disable-scroll=false&uaid=MGijX&paid=o_28299092"></iframe>"""
    },
    "Botany": {
        "Photosynthesis": """<div class="sketchfab-embed-wrapper">
        <iframe title="photosynthesis" frameborder="0" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true" 
        allow="autoplay; fullscreen; xr-spatial-tracking" 
        xr-spatial-tracking execution-while-out-of-viewport execution-while-not-rendered web-share
        style="aspect-ratio: 4 / 3; width: 100%; border:none;"
        src="https://sketchfab.com/models/447ba8d6d1b74668853fd6096ec89435/embed"></iframe></div>"""
    },
    "Circulatory System": {
        "Heart": """<iframe id="embedded-human" frameBorder="0" style="aspect-ratio: 4 / 3; width: 100%" allowFullScreen="true" loading="lazy" src="https://human.biodigital.com/viewer/?id=6Vb5&ui-anatomy-descriptions=true&ui-anatomy-pronunciations=true&ui-anatomy-labels=true&ui-audio=true&ui-chapter-list=false&ui-fullscreen=true&ui-help=true&ui-info=true&ui-label-list=true&ui-layers=true&ui-skin-layers=true&ui-loader=circle&ui-media-controls=full&ui-menu=true&ui-nav=true&ui-search=true&ui-tools=true&ui-tutorial=false&ui-undo=true&ui-whiteboard=true&initial.none=true&disable-scroll=false&uaid=MGijp&paid=o_28299092"></iframe>"""
    }
}

# --------------------------
# Routes

@app.route('/', methods=['GET', 'POST'])
def index():
    iframe_code = None
    selected_chapter = None
    selected_topic = None
    error = None

    if request.method == 'POST':
        selected_chapter = request.form.get("chapter")
        selected_topic = request.form.get("topic")
        if selected_chapter in database and selected_topic in database[selected_chapter]:
            iframe_code = database[selected_chapter][selected_topic]
        else:
            error = "⚠️ Model not available for this selection."

    chapters = list(database.keys())
    topics = list(database[selected_chapter].keys()) if selected_chapter else []

    return render_template(
        'index.html',
        chapters=chapters,
        topics=topics,
        selected_chapter=selected_chapter,
        selected_topic=selected_topic,
        iframe_code=iframe_code,
        error=error,
        database=database
    )

# --------------------------
# Optional API route for Sketchfab model info
# --------------------------
@app.route('/api/sketchfab/<model_id>')
def get_sketchfab_model(model_id):
    headers = {"Authorization": f"Token {SKETCHFAB_API_TOKEN}"}
    response = requests.get(f"https://api.sketchfab.com/v3/models/{model_id}", headers=headers)
    return jsonify(response.json())

# --------------------------
# Run the app
# --------------------------
if __name__ == '__main__':
    app.run(debug=True)