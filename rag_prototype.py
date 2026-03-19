"""
RAG Analyze Prototype
=====================
เปรียบเทียบผลการ analyze requirement ระหว่าง:
  1. Normal : ส่ง prompt ให้ Gemini โดยตรง
  2. RAG    : ค้นหา rules ที่ semantic-similar จาก DB แล้ว inject เป็น context

ข้อมูล:
  - Rules  : ดึงจาก table `rules` (embedding VECTOR(768))
  - Requirements : ดึงจาก table `origin_requirements` ตาม project ที่เลือก

Run:
  python rag_prototype.py
"""

import os
import sys
import json
import textwrap
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from embedding import embed
from google import genai

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/imreq")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash-lite"
EMBED_MODEL_NAME = "all-mpnet-base-v2"   # 768 dimensions
TOP_K_RULES = 26

# ─────────────────────────────────────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────────────────────────────────────
def get_conn():
    return psycopg2.connect(DATABASE_URL)


def list_projects() -> list:
    """แสดงรายการ projects ทั้งหมด"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.title, p.requirement_template,
               COUNT(o.id) AS req_count
        FROM projects p
        LEFT JOIN origin_requirements o ON o.project_id = p.id
        GROUP BY p.id, p.title, p.requirement_template
        ORDER BY p.created_at DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": str(r[0]), "title": r[1], "template": r[2], "req_count": r[3]} for r in rows]


def get_requirements(project_id: str) -> list:
    """ดึง requirements จาก origin_requirements ของ project"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT req_id, module, requirement
        FROM origin_requirements
        WHERE project_id = %s
        ORDER BY req_id;
    """, (project_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"req_id": r[0], "module": r[1], "requirement": r[2]} for r in rows]



def search_relevant_rules(req_embedding: list, top_k: int = TOP_K_RULES) -> list:
    """ค้นหา rules ที่ใกล้เคียงที่สุดด้วย cosine similarity"""
    conn = get_conn()
    cur = conn.cursor()
    emb_str = "[" + ",".join(str(x) for x in req_embedding) + "]"
    cur.execute(
        """
        SELECT clause, topic, rule_text,
               1 - (embedding <=> %s::vector) AS similarity
        FROM rules
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (emb_str, emb_str, top_k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"clause": r[0], "topic": r[1], "rule_text": r[2], "similarity": round(float(r[3]), 4)}
        for r in rows
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Gemini
# ─────────────────────────────────────────────────────────────────────────────
CRITERIA_MEANING = {
    "Appropriate": "Requirement level of abstraction is appropriate; avoids unnecessary design constraints.",
    "Complete":    "Sufficiently describes the need without requiring additional information.",
    "Conforming":  "Conforms to an approved template/style (e.g. EARS, ISO29148).",
    "Correct":     "Accurately represents the entity need.",
    "Feasible":    "Can be realized within system constraints (cost, schedule, technical).",
    "Necessary":   "Defines an essential capability; not obsolete or duplicated.",
    "Singular":    "States a single capability/characteristic/constraint.",
    "Unambiguous": "Can be interpreted in only one way; stated simply.",
    "Verifiable":  "Can be proven/verified; includes measurable criteria.",
}

CRITERIA_TEXT = "\n".join(
    f"{i+1}. {k}: {v}" for i, (k, v) in enumerate(CRITERIA_MEANING.items())
)

GENERATION_CONFIG = {"temperature": 0, "top_p": 1, "top_k": 1}

JSON_SCHEMA = """{
  "req_id": "<req_id>",
  "results": [
    {"criterion": "Appropriate", "pass": true|false, "reason": "<empty if passed>"},
    {"criterion": "Complete",    "pass": true|false, "reason": ""},
    {"criterion": "Conforming",  "pass": true|false, "reason": ""},
    {"criterion": "Correct",     "pass": true|false, "reason": ""},
    {"criterion": "Feasible",    "pass": true|false, "reason": ""},
    {"criterion": "Necessary",   "pass": true|false, "reason": ""},
    {"criterion": "Singular",    "pass": true|false, "reason": ""},
    {"criterion": "Unambiguous", "pass": true|false, "reason": ""},
    {"criterion": "Verifiable",  "pass": true|false, "reason": ""}
  ]
}"""


def _parse_result(text: str, req_id: str) -> dict:
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    data = json.loads(text)
    passed, failed = [], {}
    for r in data["results"]:
        if r["pass"]:
            passed.append(r["criterion"])
        else:
            failed[r["criterion"]] = r.get("reason", "ไม่ผ่านเกณฑ์")
    return {"req_id": req_id, "score": f"{len(passed)}/9", "passed": passed, "failed": failed}


def analyze_normal(client, req_id: str, requirement: str) -> dict:
    """วิธีปกติ: ไม่มี context จาก rules"""
    prompt = f"""You are a software requirement expert. Analyze this requirement against ALL 9 ISO 29148 quality criteria.

Requirement ID: {req_id}
Requirement: "{requirement}"

ISO 29148 Quality Criteria:
{CRITERIA_TEXT}

LANGUAGE RULE: respond in the SAME language as the requirement.
Return JSON only:
{JSON_SCHEMA}"""
    resp = client.models.generate_content(
        model=GEMINI_MODEL, contents=prompt, config=GENERATION_CONFIG
    )
    return _parse_result(resp.text.strip(), req_id)


def analyze_with_rag(client, req_id: str, requirement: str, relevant_rules: list) -> dict:
    """RAG: inject relevant rules เป็น context ใน prompt"""
    rules_context = "\n\n".join(
        f"[Rule {i+1} | {r['topic']} | similarity={r['similarity']}]\n"
        f"Clause: {r['clause']}\n"
        f"{r['rule_text']}"
        for i, r in enumerate(relevant_rules)
    )
    prompt = f"""You are a software requirement expert. Analyze this requirement against ALL 9 ISO 29148 quality criteria.

Requirement ID: {req_id}
Requirement: "{requirement}"

ISO 29148 Quality Criteria:
{CRITERIA_TEXT}

Relevant ISO 29148 Rules (retrieved via semantic search — use these as authoritative reference):
{rules_context}

LANGUAGE RULE: respond in the SAME language as the requirement.
Return JSON only:
{JSON_SCHEMA}"""
    resp = client.models.generate_content(
        model=GEMINI_MODEL, contents=prompt, config=GENERATION_CONFIG
    )
    return _parse_result(resp.text.strip(), req_id)


# ─────────────────────────────────────────────────────────────────────────────
# Markdown builders
# ─────────────────────────────────────────────────────────────────────────────
ALL_CRITERIA = list(CRITERIA_MEANING.keys())


def md_comparison(req: dict, normal: dict, rag: dict, rules: list) -> str:
    req_id = req["req_id"]
    requirement = req["requirement"]
    module = req.get("module") or "-"
    lines = []

    lines.append(f"## {req_id} — {module}")
    lines.append(f"> {requirement}")
    lines.append("")

    # Retrieved rules table
    lines.append("### 📚 Retrieved Rules (RAG context)")
    lines.append("| # | Topic | Similarity | Rule (excerpt) |")
    lines.append("|---|-------|-----------|----------------|")
    for i, r in enumerate(rules, 1):
        short = textwrap.shorten(r["rule_text"], width=100, placeholder="...")
        lines.append(f"| {i} | {r['topic']} | {r['similarity']} | {short} |")
    lines.append("")

    # Score summary table
    lines.append("### Score Comparison")
    lines.append("| Method | Score | Passed Criteria |")
    lines.append("|--------|-------|-----------------|")
    lines.append(f"| Normal | **{normal['score']}** | {', '.join(normal['passed']) or '–'} |")
    lines.append(f"| RAG    | **{rag['score']}** | {', '.join(rag['passed']) or '–'} |")
    lines.append("")

    # Per-criteria diff table
    lines.append("### Per-Criteria Breakdown")
    lines.append("| Criterion | Normal | RAG | Note |")
    lines.append("|-----------|--------|-----|------|")
    for c in ALL_CRITERIA:
        n_str = "✅ PASS" if c in normal["passed"] else "❌ FAIL"
        r_str = "✅ PASS" if c in rag["passed"]    else "❌ FAIL"
        note = ""
        if c in normal["passed"] and c not in rag["passed"]:
            note = "⬇ RAG stricter"
        elif c not in normal["passed"] and c in rag["passed"]:
            note = "⬆ RAG more lenient"
        lines.append(f"| {c} | {n_str} | {r_str} | {note} |")
    lines.append("")

    # Failed reasons
    has_failed = any(c in normal["failed"] or c in rag["failed"] for c in ALL_CRITERIA)
    if has_failed:
        lines.append("### Failed Reasons")
        for c in ALL_CRITERIA:
            n_r = normal["failed"].get(c)
            r_r = rag["failed"].get(c)
            if n_r or r_r:
                lines.append(f"**{c}**")
                if n_r:
                    lines.append(f"- **Normal:** {n_r}")
                if r_r:
                    lines.append(f"- **RAG:** {r_r}")
                lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def md_summary(project_id: str, results: list) -> str:
    lines = []
    lines.append("## Summary")
    lines.append(f"- **Project ID:** `{project_id}`")
    lines.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- **Total requirements:** {len(results)}")
    lines.append("")

    lines.append("| req_id | Normal | RAG | Diff |")
    lines.append("|--------|--------|-----|------|")
    total_n = total_r = 0
    for r in results:
        n_score = int(r["normal"]["score"].split("/")[0])
        r_score = int(r["rag"]["score"].split("/")[0])
        diff = r_score - n_score
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        total_n += n_score
        total_r += r_score
        lines.append(f"| {r['req_id']} | {r['normal']['score']} | {r['rag']['score']} | {diff_str} |")
    n = len(results)
    lines.append(f"| **Average** | **{total_n/n:.1f}/9** | **{total_r/n:.1f}/9** | |")
    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    project_id = "57fb6546-ab28-47d5-95d0-db4d6bdf4145"
    requirements = get_requirements(project_id)

    print(f"✅  Project : {project_id}")
    print(f"   Found   : {len(requirements)} requirements")
    print(f"   Analyzing...\n")

    client = genai.Client(api_key=GEMINI_API_KEY)

    md_sections = []
    md_sections.append("# RAG Analyze Prototype — Results\n")

    all_results = []
    for req in requirements:
        print(f"🔍  {req['req_id']} ...")

        req_emb = embed(req["requirement"])
        relevant_rules = search_relevant_rules(req_emb, top_k=TOP_K_RULES)

        print("    ├─ Normal analyze ...")
        normal = analyze_normal(client, req["req_id"], req["requirement"])

        print("    └─ RAG analyze ...")
        rag = analyze_with_rag(client, req["req_id"], req["requirement"], relevant_rules)

        all_results.append({"req_id": req["req_id"], "normal": normal, "rag": rag, "req": req, "rules": relevant_rules})
        md_sections.append(md_comparison(req, normal, rag, relevant_rules))

    md_sections.append(md_summary(project_id, all_results))

    out_path = os.path.join(os.path.dirname(__file__), "rag_result.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_sections))

    print(f"\n✅  Done. Report saved to: {out_path}")


if __name__ == "__main__":
    main()
