import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv
from PIL import Image
from bs4 import BeautifulSoup
from manim import *
import subprocess

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def verify_biology_relevance(topic, summary, image_url):
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY not found.")
        return False
    try:
        GEMINI_API_URL = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.5-flash:generateContent"
        )
        headers = {"Content-Type": "application/json"}
        params = {"key": GEMINI_API_KEY}
        prompt = f"""
        You are a biology expert. Analyze the following Wikipedia summary and image.
        Respond only 'yes' if the image is biologically relevant; otherwise respond 'no'.
        Topic: {topic}
        Summary: {summary}
        Image URL: {image_url}
        """
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
        r.raise_for_status()
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip().lower()
        return "yes" in text
    except Exception as e:
        print("Gemini verification error:", e)
        return False

def fetch_wikipedia_images(topic):
    topic = topic.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{topic}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    imgs = soup.find_all("img")
    img_urls = []
    for img in imgs:
        src = img.get("src")
        if not src:
            continue
        if src.startswith("//"):
            src = "https:" + src
        if any(ext in src.lower() for ext in [".gif", ".jpg", ".jpeg", ".png"]):
            img_urls.append(src)
    return img_urls

def download_images(topic, img_urls):
    os.makedirs("images", exist_ok=True)
    priority_ext = [".gif", ".jpg", ".jpeg", ".png"]
    downloaded_files = []
    for ext in priority_ext:
        for url in img_urls:
            if url.lower().endswith(ext):
                fname = f"images/{topic}_{len(downloaded_files)}{ext}"
                headers = {"User-Agent": "Mozilla/5.0"}
                try:
                    r = requests.get(url, headers=headers)
                    if r.status_code == 200:
                        with open(fname, "wb") as f:
                            f.write(r.content)
                        downloaded_files.append(fname)
                except Exception as e:
                    print(f"Skip {url}: {e}")
    return downloaded_files

def prepare_frames(downloaded_files):
    media_dict = {}
    os.makedirs("frames", exist_ok=True)
    count = 0
    for f in downloaded_files:
        if f.lower().endswith(".gif"):
            frames_dir = f"frames/gif_{count}"
            os.makedirs(frames_dir, exist_ok=True)
            gif = Image.open(f)
            frame_count = 0
            try:
                while True:
                    frame = gif.copy()
                    frame_path = os.path.join(frames_dir, f"frame_{frame_count:03d}.png")
                    frame.save(frame_path)
                    frame_count += 1
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass
            media_dict[f] = frames_dir
        else:
            media_dict[f] = f
        count += 1
    return media_dict

def generate_manim_script(media_dict, output_script="PlayWikiMedia.py"):
    class_name = "PlayWikiMedia"
    code_lines = [
        "from manim import *",
        "import os",
        "",
        f"class {class_name}(Scene):",
        "    def construct(self):",
        "        # Sequentially display media sources"
    ]

    for fname, path in media_dict.items():
        if os.path.isdir(path):  # GIF frames
            code_lines.append(f"        frames_dir = r'{path}'")
            code_lines.append("        frame_files = sorted(os.listdir(frames_dir))")
            code_lines.append("        frame_files = [f for f in frame_files if f.endswith('.png')]")
            code_lines.append("        for f in frame_files:")
            code_lines.append("            img = ImageMobject(os.path.join(frames_dir, f))")
            code_lines.append("            self.add(img)")
            code_lines.append("            self.wait(0.05)")
            code_lines.append("            self.remove(img)")
        else:  # Static images
            code_lines.append(f"        img = ImageMobject(r'{path}')")
            code_lines.append("        self.add(img)")
            code_lines.append("        self.wait(1)")
            code_lines.append("        self.remove(img)")

    with open(output_script, "w") as f:
        f.write("\n".join(code_lines))
    print(f"✅ Generated Manim script: {output_script}")
    return output_script, class_name

def main():
    topic = input("Enter a biology topic: ").strip()

    # Wikipedia summary
    encoded_topic = quote(topic)
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_topic}"
    headers = {"User-Agent": "Mozilla/5.0"}
    summary = ""
    try:
        res = requests.get(summary_url, headers=headers)
        res.raise_for_status()
        summary = res.json().get("extract", "")
    except Exception as e:
        print("⚠️ Could not fetch summary:", e)

    # Fetch & verify images
    img_urls = fetch_wikipedia_images(topic)
    if not img_urls:
        print("❌ No images found.")
        return

    verified_images = []
    for img_url in img_urls:
        if verify_biology_relevance(topic, summary, img_url):
            verified_images.append(img_url)

    if len(verified_images) < 3:
        print("⚠️ Less than 3 biologically relevant images found. Will use all available.")

    print(f"✅ {len(verified_images)} biologically relevant images found.")

    # Download images
    downloaded_files = download_images(topic, verified_images)
    if not downloaded_files:
        print("❌ No downloadable images.")
        return

    # Convert GIFs to frames & prepare media dict
    media_dict = prepare_frames(downloaded_files)

    # Generate Manim script
    script_file, class_name = generate_manim_script(media_dict)

    # Run Manim
    print(f"\n🎬 Rendering animation with Manim...")
    subprocess.run(["manim", "-pql", script_file, class_name])

if __name__ == "__main__":
    main()