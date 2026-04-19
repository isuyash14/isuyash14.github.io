import re

with open("intel.html", "r") as f:
    text = f.read()

# Replace the summary styling and text
old_summary = """<summary style="font-family: 'IBM Plex Mono'; font-size: .65rem; color: var(--amber); letter-spacing: .1em; cursor: pointer; outline: none; list-style: none;">
              ▶ SHOW EXPERT ANSWER
            </summary>"""

new_summary = """<summary style="font-family: 'Open Sans', sans-serif; font-size: 0.95rem; font-weight: normal; color: var(--amber); cursor: pointer; outline: none; list-style: none; display: flex; align-items: center; gap: 0.5rem;">
              ▶ Show expert answer
            </summary>"""

# Also handle any variations of spaces
# We can use regex to replace all summary tags inside details that have ▶ SHOW EXPERT ANSWER
text = re.sub(
    r'<summary[^>]*>\s*▶ SHOW EXPERT ANSWER\s*</summary>', 
    new_summary, 
    text
)

# We also want to remove <strong> tags from the bullets
# We can find all the inner <ul> elements within the background: rgba(0,0,0,0.2) block
# Actually, an easier way is to just find all <li style="margin-bottom: .75rem;"><strong>...</strong>: and replace with <li style="margin-bottom: .75rem;">...:
text = text.replace("<strong>", "")
text = text.replace("</strong>", "")

# Oh, wait! There are <strong> elements in the Prompt and Hint sections too:
# <p><strong>Prompt:</strong> ...</p>
# <p><strong>Hint:</strong> ...</p>
# <p class="q-companies"><strong>Tagged at:</strong> ...</p>
# The user said "not all capitalized adn bolded. it should be normal oppen sans font"
# Did they mean the summary button itself, or everything? 
# "Show expert answer
# make it detailed and have bullet points
# not all capitalized adn bolded. it should be normal oppen sans font"
# This definitely refers to the "Show expert answer" text and perhaps the bullets.
# So I should ONLY remove <strong> from the bullets, or maybe put them back for Prompt/Hint if I blindly replace.

with open("intel.html", "r") as f:
    text = f.read()

# Fix the summary
text = re.sub(
    r'<summary[^>]*>\s*▶ SHOW EXPERT ANSWER\s*</summary>', 
    new_summary, 
    text
)

# To remove <strong> inside the inner details, we can find the block <details style="margin-top: 1.5rem; ..."> ... </details>
# and strip <strong> from it.
def repl(m):
    return m.group(0).replace("<strong>", "").replace("</strong>", "")

text = re.sub(r'<div style="margin-top: 1rem;">\s*<ul.*?>.*?</ul>\s*</div>', repl, text, flags=re.DOTALL)

with open("intel.html", "w") as f:
    f.write(text)

print("SUCCESS")
