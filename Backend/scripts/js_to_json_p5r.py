#!/usr/bin/env python3
# Usage:
#   python scripts/js_to_json_p5r.py --source ./data --out ./data
# Requires: pip install json5

import argparse, re, json, sys
from pathlib import Path
import json5

ROYAL_FILES = {
    "data5":   "Data5Royal.js",        # arcana2CombosRoyal, specialCombosRoyal
    "persona": "PersonaDataRoyal.js",  # personaMapRoyal
}

def extract_js_rhs(text: str, varname: str) -> str:
    m = re.search(rf"(?:var|let|const)\s+{re.escape(varname)}\s*=\s*", text)
    if not m:
        raise ValueError(f"Variable {varname} not found")
    i = m.end()
    while i < len(text) and text[i] in " \t\r\n":
        i += 1
    if i >= len(text) or text[i] not in "{[":
        raise ValueError(f"{varname}: expected object/array literal after '='")
    opener = text[i]; closer = "}" if opener == "{" else "]"
    depth = 0; j = i; in_str = False; str_ch = ""; esc = False
    while j < len(text):
        ch = text[j]
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == str_ch: in_str = False
        else:
            if ch in ("'", '"'): in_str = True; str_ch = ch
            elif ch == opener:  depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0: j += 1; break
        j += 1
    if depth != 0:
        raise ValueError(f"{varname}: unbalanced brackets")
    return text[i:j]

def main():
    ap = argparse.ArgumentParser(description="Convert persona5_calculator Royal JS data → JSON.")
    ap.add_argument("--source", required=True, help="Folder with Data5Royal.js & PersonaDataRoyal.js")
    ap.add_argument("--out", default="data", help="Destination folder for JSON (default: ./data)")
    args = ap.parse_args()

    src = Path(args.source); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    data5 = src / ROYAL_FILES["data5"]
    persona = src / ROYAL_FILES["persona"]
    missing = [str(p) for p in (data5, persona) if not p.exists()]
    if missing:
        print("Missing:", ", ".join(missing)); sys.exit(1)

    txt_data5 = data5.read_text(encoding="utf-8")
    arcana2  = json5.loads(extract_js_rhs(txt_data5, "arcana2CombosRoyal"))
    specials = json5.loads(extract_js_rhs(txt_data5, "specialCombosRoyal"))

    txt_persona = persona.read_text(encoding="utf-8")
    persona_map = json5.loads(extract_js_rhs(txt_persona, "personaMapRoyal"))  # {name: info}

    # normalize to list for our pipeline
    personae = []
    for name, info in (persona_map or {}).items():
        if not isinstance(info, dict): continue
        lvl = info.get("lvl") or info.get("level") or info.get("baseLevel") or 0
        try: lvl = int(lvl)
        except: pass
        personae.append({
            "name": name,
            "arcana": info.get("arcana") or "Unknown",
            "level": lvl,
            "inherits": info.get("inherits"),
            "special": bool(info.get("special")),
            "rare": bool(info.get("rare")),
            "dlc": bool(info.get("dlc")),
            "skills": info.get("skills", {}),
        })

    (out / "personae.json").write_text(json.dumps(personae, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "fusion-chart.json").write_text(json.dumps(arcana2, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "special-recipes.json").write_text(json.dumps(specials, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ Wrote {len(personae)} personae")
    print(f"✅ Wrote fusion chart ({len(arcana2)} arcanas)")
    print(f"✅ Wrote special recipes ({len(specials)})")

if __name__ == "__main__":
    main()
