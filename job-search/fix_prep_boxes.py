with open("index.html", "r") as f:
    text = f.read()

# 1. Update CSS
css_to_add = """    .hero-right {
      display: flex; flex-direction: column; gap: 2rem;
      padding-right: 2.5rem; /* Push left from right edge */
      margin-left: -1rem; /* Nudge slightly left */
    }

    .prep-box {
      background: var(--bg-card); 
      border: 1px solid var(--border-b); 
      padding: 2rem; 
      position: relative; 
      overflow: hidden;
      border-radius: 4px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
      transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s;
    }
    .prep-box:hover {
      transform: translateY(-4px);
      box-shadow: 0 16px 40px rgba(0,0,0,0.6);
      border-color: rgba(255,255,255,0.2);
    }
    .prep-box:hover .accent-bar-blue { box-shadow: 0 0 16px var(--blue); }
    .prep-box:hover .accent-bar-amber { box-shadow: 0 0 16px var(--amber); }

    .accent-bar-blue { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: var(--blue); transition: box-shadow 0.3s;}
    .accent-bar-amber { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: var(--amber); transition: box-shadow 0.3s;}
"""

text = text.replace("""    .hero-right {
      display: flex; flex-direction: column; gap: 2rem;
    }""", css_to_add)

# 2. Update HTML inline styles
old_blue_box = """<div class="prep-box" style="background: var(--bg-card); border: 1px solid var(--border-b); padding: 2rem; position: relative; overflow: hidden;">
          <div style="content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: var(--blue);"></div>"""

new_blue_box = """<div class="prep-box">
          <div class="accent-bar-blue"></div>"""

text = text.replace(old_blue_box, new_blue_box)

old_amber_box = """<div class="prep-box" style="background: var(--bg-card); border: 1px solid var(--border-b); padding: 2rem; position: relative; overflow: hidden;">
          <div style="content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: var(--amber);"></div>"""

new_amber_box = """<div class="prep-box">
          <div class="accent-bar-amber"></div>"""

text = text.replace(old_amber_box, new_amber_box)

with open("index.html", "w") as f:
    f.write(text)

print("SUCCESS")
