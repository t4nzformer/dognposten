import openai
import feedparser
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Correct RSS Feeds per Category ---
feeds = {
    "🇳🇴 Innenriks": "https://www.nrk.no/norge/toppsaker.rss",
    "🌍 Utenriks": "https://www.nrk.no/urix/toppsaker.rss",
    "🎭 Kultur": "https://www.nrk.no/kultur/toppsaker.rss"
}

def summarize(text):
    prompt = (
        "Oppsummer denne norske nyhetssaken i 1–3 rolige, nøkterne setninger. "
        "Ikke bruk clickbait. Ikke bruk sensasjonelle ord. Skriv tydelig, informativt og rolig.\n\n"
        + text
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=120
    )
    return response.choices[0].message.content.strip()

# --- Collect summaries per category ---
sections = {}
for section, url in feeds.items():
    feed = feedparser.parse(url)
    entries = feed.entries[:3]
    summaries = []
    for entry in entries:
        content = entry.title + "\n\n" + entry.summary
        summaries.append(summarize(content))
        time.sleep(20)  # Respect 3 RPM rate limit
    sections[section] = summaries

# --- Format date in Norwegian ---
month_map = {
    "January": "januar", "February": "februar", "March": "mars", "April": "april",
    "May": "mai", "June": "juni", "July": "juli", "August": "august",
    "September": "september", "October": "oktober", "November": "november", "December": "desember"
}
now = datetime.now()
day = now.strftime("%d.")
month = month_map[now.strftime("%B")]
year = now.strftime("%Y")
formatted_date = f"{day} {month} {year}"

# --- Generate HTML ---
html_output = f"""<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <title>Døgnposten</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Døgnposten – Rolige nyheter, én gang om dagen.">
  <style>
    body {{
      font-family: Georgia, serif;
      background-color: #f7f7f7;
      color: #111;
      margin: 4em auto;
      max-width: 640px;
      padding: 0 1em;
      line-height: 1.6;
    }}
    h1 {{
      font-size: 2em;
      margin-bottom: 0.2em;
    }}
    .subtitle {{
      font-size: 1em;
      color: #555;
      margin-bottom: 2em;
    }}
    .date {{
      font-size: 1em;
      font-weight: bold;
      margin-bottom: 2em;
    }}
    h2 {{
      font-size: 1.2em;
      margin-top: 2em;
      margin-bottom: 0.5em;
    }}
    ul {{
      list-style-type: disc;
      padding-left: 1.5em;
    }}
  </style>
</head>
<body>
  <h1>Døgnposten</h1>
  <div class="subtitle">Rolige nyheter, én gang om dagen</div>
  <div class="date">{formatted_date}</div>
"""

# --- Add news sections to HTML ---
for section, items in sections.items():
    html_output += f"\n  <h2>{section}</h2>\n  <ul>\n"
    for summary in items:
        html_output += f"    <li>{summary}</li>\n    <br/>\n"
    html_output += "  </ul>\n"

html_output += """
</body>
</html>
"""

# --- Save to index.html ---
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)
