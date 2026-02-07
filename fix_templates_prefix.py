# fix_templates_prefix.py
import re, pathlib, shutil

TEMPLATE_DIR = pathlib.Path("app/templates")
# endpoints that should be namespace-prefixed with 'main'
ENDPOINTS = [
    "login","logout","signup","patient_dashboard","doctor_dashboard","pharmacy_dashboard",
    "book_appointment","approve_appointment","reject_appointment","create_prescription",
    "notifications","mark_notifications_read","home"
]

def replace_in_text(text):
    # safe replace: only replace url_for('X') that are NOT already main.X
    def repl(m):
        name = m.group(1)
        if name.startswith("main."):
            return m.group(0)  # already namespaced
        if name in ENDPOINTS:
            return "url_for('main.%s')" % name
        return m.group(0)

    return re.sub(r"url_for\(\s*'([^']+)'\s*\)", repl, text)

files_changed = []
for p in TEMPLATE_DIR.rglob("*.html"):
    txt = p.read_text(encoding="utf8")
    new = replace_in_text(txt)
    if new != txt:
        bak = p.with_suffix(p.suffix + ".bak")
        shutil.copyfile(p, bak)
        p.write_text(new, encoding="utf8")
        files_changed.append(str(p))

print("Patched files:", files_changed)
if not files_changed:
    print("No changes made (templates already use 'main.' prefix or matched endpoints not found).")
