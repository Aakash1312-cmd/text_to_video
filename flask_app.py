from flask import Flask, render_template, request
import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote  # for URL encoding

# Load environment variables
load_dotenv()
SKETCHFAB_API_TOKEN = os.getenv("SKETCHFAB_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

# ------------------------
# Verify biology relevance using Gemini 2.5 Flash
# ------------------------
def verify_biology_relevance(topic, summary, image_url):
    try:
        if not GEMINI_API_KEY:
            print("⚠️ GEMINI_API_KEY not found in environment.")
            return False

        GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": GEMINI_API_KEY}

        prompt = f"""
        You are a biology expert. Analyze the following topic and image description.
        Determine if it is biologically relevant or not.
        Respond strictly with 'yes' or 'no'.
        Topic: {topic}
        Summary: {summary}
        Image URL: {image_url}
        """

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
        response.raise_for_status()

        output = response.json()
        reply = output["candidates"][0]["content"]["parts"][0]["text"].strip().lower()
        return "yes" in reply

    except Exception as e:
        print("Gemini agent error:", e)
        return False

# ------------------------
# Function to fetch image from Wikipedia using REST API + Gemini Agent filter
# ------------------------
def fetch_wikipedia_image(topic):
    try:
        encoded_topic = quote(topic)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_topic}"
        response = requests.get(url, headers={"User-Agent": "3D-Anatomy-Viewer/1.0"})
        data = response.json()

        summary = data.get("extract", "")
        image_url = None

        if "originalimage" in data and "source" in data["originalimage"]:
            image_url = data["originalimage"]["source"]
        elif "thumbnail" in data and "source" in data["thumbnail"]:
            image_url = data["thumbnail"]["source"]

        # If we have an image, verify if it's biologically relevant
        if image_url:
            if verify_biology_relevance(topic, summary, image_url):
                return image_url
            else:
                print("⚠️ Image not biologically relevant — fallback used.")
                return "/static/biology_default.jpg"

        print("⚠️ No image found on Wikipedia.")
        return "/static/biology_default.jpg"

    except Exception as e:
        print("Wikipedia fetch error:", e)
        return "/static/biology_default.jpg"

# ------------------------
# Flask route
# ------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    iframe_code = None
    search_query = None
    error = None
    fallback_image = None

    if request.method == 'POST':
        search_query = request.form.get("search_query", "").strip()
        found = False

        # Search database
        for chapter, topics in database.items():
            for topic, iframe in topics.items():
                if search_query.lower() in chapter.lower() or search_query.lower() in topic.lower():
                    iframe_code = iframe
                    found = True
                    break
            if found:
                break

        # Fallback: Wikipedia image (biologically verified)
        if not found:
            fallback_image = fetch_wikipedia_image(search_query)
            if fallback_image and "biology_default.jpg" not in fallback_image:
                error = f"⚠️ 3D model not found. Showing biology image from Wikipedia for '{search_query}'."
            else:
                error = f"⚠️ Model not available. Showing biology fallback image for '{search_query}'."

    return render_template(
        'index.html',
        iframe_code=iframe_code,
        search_query=search_query,
        error=error,
        fallback_image=fallback_image
    )

if __name__ == '__main__':
    app.run(debug=True)