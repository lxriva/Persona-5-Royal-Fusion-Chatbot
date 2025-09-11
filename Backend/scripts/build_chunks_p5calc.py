#!/usr/bin/env python3
import json, os, math
from pathlib import Path
from typing import Dict, List, Any, Tuple

DATA_DIR = Path("data")
OUT_DIR = Path("chunks")

PERSONAE_FILE = DATA_DIR / "personae.json"
FUSION_CHART_FILE = DATA_DIR / "fusion-chart.json"
SPECIAL_RECIPES_FILE = DATA_DIR / "special-recipes.json"

def load_json(p: Path):
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def is_true(x) -> bool:
    return bool(x) is True

def persona_name(p: Dict[str,Any]) -> str:
    return p.get("name") or p.get("Name") or "Unknown"

def persona_level(p: Dict[str,Any]) -> int:
    lvl = p.get("lvl") or p.get("level") or p.get("baseLevel") or 0
    try:
        return int(lvl)
    except Exception:
        return 0

def persona_arcana(p: Dict[str,Any]) -> str:
    return p.get("arcana") or p.get("Arcana") or "Unknown"

def is_special_or_rare_or_dlc(p: Dict[str,Any]) -> bool:
    flags = [p.get("special"), p.get("Special"), p.get("rare"), p.get("Rare"), p.get("dlc"), p.get("DLC")]
    note = (p.get("note") or p.get("Note") or "").lower()
    return any(is_true(v) for v in flags) or ("special" in note)

def build_arcana_lists(personae: List[Dict[str,Any]]) -> Dict[str, List[Dict[str,Any]]]:
    per_arc: Dict[str, List[Dict[str,Any]]] = {}
    for p in personae:
        per_arc.setdefault(persona_arcana(p), []).append(p)
    for plist in per_arc.values():
        plist.sort(key=persona_level)
    return per_arc

def compute_result_persona(a: Dict[str,Any], b: Dict[str,Any],
                           chart: Dict[str,Dict[str,str]],
                           per_arc_sorted: Dict[str,List[Dict[str,Any]]]) -> Dict[str,Any] | None:
    arc_a, arc_b = persona_arcana(a), persona_arcana(b)
    if arc_a not in chart or arc_b not in chart[arc_a]:
        return None
    result_arc = chart[arc_a][arc_b]
    target = math.floor((persona_level(a) + persona_level(b)) / 2) + 1
    candidates = per_arc_sorted.get(result_arc, [])
    if not candidates:
        return None
    idx = None
    for i, p in enumerate(candidates):
        if persona_level(p) >= target:
            idx = i; break
    if idx is None: idx = 0
    a_name, b_name = persona_name(a), persona_name(b)
    seen = 0
    while seen < len(candidates) and (persona_name(candidates[idx]) in (a_name, b_name)):
        idx = (idx + 1) % len(candidates); seen += 1
    if seen >= len(candidates): return None
    return candidates[idx]

def _as_list(x) -> List[str]:
    if x is None: return []
    if isinstance(x, (list, tuple)): return [str(s) for s in x]
    if isinstance(x, dict): return [str(k) for k in x.keys()]
    return [str(x)]

def normalize_specials(specials_raw: Any) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    if isinstance(specials_raw, dict):
        for result, comps in specials_raw.items():
            out[str(result)] = _as_list(comps)
        return out
    if isinstance(specials_raw, list):
        for item in specials_raw:
            if isinstance(item, dict):
                if len(item) == 1 and all(isinstance(k, str) for k in item.keys()):
                    k = list(item.keys())[0]; out[str(k)] = _as_list(item[k]); continue
                name = item.get("name") or item.get("result") or item.get("resultName")
                comps = item.get("sources") or item.get("components") or item.get("ingredients") or item.get("recipe")
                if name: out[str(name)] = _as_list(comps); continue
            elif isinstance(item, (list, tuple)) and item and isinstance(item[0], str):
                out[str(item[0])] = [str(x) for x in item[1:]]; continue
        return out
    return out

def build_all_normal_pairs(personae: List[Dict[str,Any]], chart: Dict[str,Dict[str,str]]):
    comps = [p for p in personae if not is_special_or_rare_or_dlc(p)]
    per_arc_sorted = build_arcana_lists([p for p in personae if not is_true(p.get("dlc"))])
    results_map: Dict[str, List[Tuple[str,str]]] = {}
    used_in_normal: Dict[str, List[Tuple[str,str]]] = {}
    n = len(comps)
    for i in range(n):
        for j in range(i+1, n):
            a, b = comps[i], comps[j]
            res = compute_result_persona(a, b, chart, per_arc_sorted)
            if not res: continue
            res_name = persona_name(res)
            pair = (persona_name(a), persona_name(b))
            results_map.setdefault(res_name, []).append(pair)
            used_in_normal.setdefault(pair[0], []).append(pair)
            used_in_normal.setdefault(pair[1], []).append(pair)
    return results_map, used_in_normal

def main():
    if not PERSONAE_FILE.exists() or not FUSION_CHART_FILE.exists() or not SPECIAL_RECIPES_FILE.exists():
        raise SystemExit("Missing input files in ./data/ (need personae.json, fusion-chart.json, special-recipes.json)")

    personae = load_json(PERSONAE_FILE)
    chart    = load_json(FUSION_CHART_FILE)
    specials_raw = load_json(SPECIAL_RECIPES_FILE)
    specials = normalize_specials(specials_raw)

    print(f"Loaded {len(personae)} personae; fusion-chart arcs: {len(chart)}; specials: {len(specials)}")
    print("Computing all normal two-way fusion outcomes...")

    results_map, used_in_normal = build_all_normal_pairs(personae, chart)

    used_in_special: Dict[str, List[str]] = {}
    for result_name, comps in specials.items():
        for comp in comps:
            used_in_special.setdefault(comp, []).append(result_name)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    def fmt_skills(p: Dict[str,Any]) -> str:
        skills = p.get("skills", [])
        if isinstance(skills, dict):
            def lv(v):
                try: return int(v)
                except Exception: return 999
            pairs = sorted(skills.items(), key=lambda kv: (lv(kv[1]), kv[0]))
            lines = [f"{k} (Lv {v})" for k,v in pairs]
        elif isinstance(skills, list):
            lines = [str(s) for s in skills]
        elif isinstance(skills, str):
            lines = [s.strip() for s in skills.split(",")]
        else:
            lines = []
        return "None listed" if not lines else "\n  - " + "\n  - ".join(lines)

    for p in personae:
        name   = persona_name(p)
        arcana = persona_arcana(p)
        lvl    = persona_level(p)
        inherits = p.get("inherits") or p.get("Inherits") or "-"
        special_flag = is_true(p.get("special"))
        dlc_flag     = is_true(p.get("dlc"))
        rare_flag    = is_true(p.get("rare"))

        lines = [
            f"Persona Name: {name}",
            f"Arcana: {arcana}",
            f"Base Level: {lvl}",
            f"Inherits: {inherits}",
            f"Special Fusion Persona: {bool(special_flag)}",
            f"DLC: {bool(dlc_flag)}  Rare: {bool(rare_flag)}",
            f"Skills:{fmt_skills(p)}",
        ]

        if name in specials and specials[name]:
            lines.append("Special Fusion Recipe: " + ", ".join(specials[name]))
        else:
            lines.append("Special Fusion Recipe: -")

        pairs = results_map.get(name, [])
        pairs_txt = "-" if not pairs else "; ".join([f"{a} + {b}" for a,b in sorted(set(pairs))][:30])
        lines.append("Normal fusion pairs that produce this persona: " + pairs_txt)

        used_norm = used_in_normal.get(name, [])
        used_norm_txt = "; ".join([f"{a} + {b}" for a,b in sorted(set(used_norm))][:20]) or "-"
        used_spec = used_in_special.get(name, [])
        used_spec_txt = ", ".join(sorted(set(used_spec))) or "-"
        lines.append("Normal fusions where this persona is a component: " + used_norm_txt)
        lines.append("Special fusions where this persona is a component: " + used_spec_txt)

        out_path = OUT_DIR / f"{name.replace('/', '-')}.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    print(f"✅ Wrote chunks to {OUT_DIR} (count={len(list(OUT_DIR.glob('*.txt')))})")

if __name__ == "__main__":
    main()
