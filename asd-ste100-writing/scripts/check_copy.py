#!/usr/bin/env python3
"""
check_copy.py — mechanical ASD-STE100 + benefit-framing checker for product copy.

Usage:
    python check_copy.py FILE [--mode procedural|descriptive|marketing] [--json]
    cat draft.md | python check_copy.py - --mode marketing

Catches the mechanical violations only. Terminology consistency, benefit framing
quality, and truthfulness still need a human (or a careful model) pass.

Stdlib only. No install.
"""

import argparse
import json
import re
import sys
from collections import defaultdict

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

MODES = {
    "procedural": {"sentence_max": 20, "para_max": 6},
    "descriptive": {"sentence_max": 25, "para_max": 6},
    "marketing": {"sentence_max": 25, "para_max": 3},
}

HEADLINE_MAX = 12

# word -> suggested replacement
SWAPS = {
    "utilize": "use", "utilise": "use", "utilizing": "use", "utilization": "use",
    "employ": "use", "leverage": "use / rewrite", "leveraging": "rewrite",
    "ensure": "make sure that", "ensures": "makes sure that", "ensuring": "rewrite",
    "verify": "make sure that", "perform": "do", "performs": "does",
    "execute": "do", "conduct": "do", "commence": "start", "initiate": "start",
    "terminate": "stop", "cease": "stop", "halt": "stop",
    "obtain": "get", "acquire": "get", "procure": "buy",
    "provide": "give", "provides": "gives", "providing": "rewrite",
    "assist": "help", "assists": "helps", "facilitate": "help", "aid": "help",
    "require": "need", "requires": "needs", "necessitate": "need",
    "indicate": "show", "indicates": "shows", "illustrate": "show",
    "modify": "change", "alter": "change", "adjust": "change",
    "maintain": "keep", "locate": "find", "identify": "find",
    "attempt": "try", "endeavor": "try", "endeavour": "try",
    "permit": "let", "allow": "let", "allows": "lets", "enable": "let",
    "enables": "lets", "purchase": "buy", "request": "ask",
    "transmit": "send", "forward": "send", "eliminate": "remove",
    "replicate": "copy", "implement": "do / install", "accommodate": "hold / fit",
    "additionally": "also", "furthermore": "also", "moreover": "also",
    "whilst": "while", "thus": "so", "hence": "so", "therefore": "so",
    "approximately": "about", "circa": "about",
    "sufficient": "enough", "adequate": "enough", "excessive": "too much",
    "numerous": "many / the number", "multitude": "many",
    "majority": "most", "substantially": "give the number",
    "significantly": "give the number", "virtually": "almost",
    "essentially": "delete", "optimal": "best", "optimum": "best",
    "minimal": "small / the number",
    "solution": "the product name / what it is",
    "solutions": "the product name / what it is",
    "offering": "the product name", "functionality": "what it does (verb)",
    "capabilities": "what it does (verb)", "methodology": "method",
    "ecosystem": "rewrite", "individuals": "people", "personnel": "staff",
    "prerequisites": "what you need first",
    "shall": "must / will", "may": "can (ability) or we allow (permission)",
    "should": "we recommend that you",
    "obviously": "delete", "clearly": "delete", "basically": "delete",
    "actually": "delete", "literally": "delete", "very": "delete",
    "really": "delete", "quite": "delete", "rather": "delete",
    "somewhat": "delete", "simply": "delete", "just": "delete",
    "easily": "delete or prove it",
}

MULTIWORD_SWAPS = {
    "prior to": "before", "in order to": "to", "subsequent to": "after",
    "due to the fact that": "because", "owing to the fact that": "because",
    "in the event that": "if", "with regard to": "about",
    "in respect of": "about", "in conjunction with": "with",
    "by means of": "with", "in the vicinity of": "near",
    "in excess of": "more than", "a minimum of": "at least",
    "the majority of": "most", "a variety of": "different / list them",
    "a range of": "different / list them", "at the end of the day": "delete",
    "when it comes to": "delete", "in terms of": "delete",
    "the fact that": "that", "needless to say": "delete",
    "that being said": "but", "and/or": "pick one, or write both",
    "out of the box": "rewrite (idiom)", "heavy lifting": "rewrite (idiom)",
    "under the hood": "rewrite (idiom)", "low-hanging fruit": "rewrite (idiom)",
    "moving the needle": "rewrite (idiom)", "best of breed": "rewrite",
    "focus on what matters": "rewrite (bolt-on benefit)",
    "peace of mind": "OK if earned - make sure the mechanism is named",
}

MARKETING_FILLER = {
    "seamless", "seamlessly", "frictionless", "effortless", "effortlessly",
    "robust", "powerful", "cutting-edge", "state-of-the-art", "best-in-class",
    "world-class", "industry-leading", "next-generation", "revolutionary",
    "game-changing", "disruptive", "innovative", "transformative",
    "unparalleled", "turnkey", "holistic", "synergy", "enterprise-grade",
    "military-grade", "blazing-fast", "lightning-fast", "supercharge",
    "turbocharge", "unlock", "unleash", "empower", "empowers", "elevate",
    "reimagine", "redefine", "delight", "magical", "magic", "obsess",
    "bespoke", "curated", "artisanal", "handcrafted", "premier",
}

BE_FORMS = {"is", "are", "was", "were", "be", "been", "being", "am"}

IRREGULAR_PARTICIPLES = {
    "made", "done", "sent", "built", "kept", "held", "found", "given",
    "taken", "written", "shown", "set", "put", "run", "read", "paid",
    "sold", "told", "brought", "caught", "chosen", "driven", "known",
    "lost", "meant", "met", "seen", "spent", "understood", "won",
}

PERFECT_MARKERS = {"have", "has", "had"}

# Words ending in -ing that are legitimate technical names or nouns.
ING_ALLOWLIST = {
    "booking", "bookings", "landing", "listing", "listings", "pricing",
    "onboarding", "billing", "marketing", "engineering", "training",
    "meeting", "meetings", "building", "buildings", "morning", "evening",
    "everything", "anything", "something", "nothing", "during", "string",
    "thing", "things", "king", "ring", "spring", "wing", "ceiling",
    "heading", "headings", "setting", "settings", "warning", "warnings",
    "rating", "ratings", "logging", "caching", "routing", "hosting",
    "cleaning", "parking", "shipping", "streaming", "staging",
}

# Function words used to detect noun clusters: a run of tokens with none of
# these in it, 4+ long, is a likely noun stack.
FUNCTION_WORDS = {
    "a", "an", "the", "and", "or", "but", "of", "in", "on", "at", "to",
    "for", "with", "by", "from", "as", "into", "over", "under", "after",
    "before", "if", "when", "while", "that", "which", "who", "this",
    "these", "those", "it", "its", "you", "your", "we", "our", "they",
    "their", "he", "she", "his", "her", "not", "no", "all", "any",
    "each", "every", "some", "so", "than", "then", "there", "here",
    "is", "are", "was", "were", "be", "been", "being", "am", "do",
    "does", "did", "can", "will", "must", "have", "has", "had", "up",
    "out", "off", "down", "about", "between", "through", "more", "most",
    "less", "one", "two", "three", "also", "only", "just", "how", "what",
    "why", "where", "now", "new", "get", "gets", "make", "makes", "use",
    "uses", "see", "sees", "keep", "keeps", "let", "lets", "need", "needs",
}

BENEFIT_SIGNALS = {
    "freedom", "free", "yourself", "own", "yours", "peace", "never",
    "stop", "safe", "sure", "certain", "minutes", "seconds", "hours",
    "days", "time", "faster", "quicker", "instead", "without", "no",
    "control", "anywhere", "anytime", "keep", "power",
}

SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'(])')
ABBREV = re.compile(r'\b(e\.g|i\.e|etc|vs|Inc|Ltd|Dr|Mr|Mrs|Ms|St|approx|Fig|No)\.$')
TOKEN = re.compile(r"[A-Za-z][A-Za-z'\-]*")


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def strip_markup(line):
    """Remove markdown/HTML noise so word counts reflect prose."""
    line = re.sub(r'`[^`]*`', ' ', line)
    line = re.sub(r'<[^>]+>', ' ', line)
    line = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', line)
    line = re.sub(r'[*_#>|]+', ' ', line)
    return line


def is_code_fence(line):
    return line.strip().startswith("```")


def split_sentences(text):
    parts = SENTENCE_SPLIT.split(text)
    merged = []
    for part in parts:
        if merged and ABBREV.search(merged[-1]):
            merged[-1] = merged[-1] + " " + part
        else:
            merged.append(part)
    return [p.strip() for p in merged if p.strip()]


def words(sentence):
    return TOKEN.findall(sentence)


def parse(text):
    """Return (blocks, sentences). Each sentence: dict with line, text, is_heading."""
    lines = text.split("\n")
    sentences = []
    blocks = []
    current_block = []
    in_fence = False

    for idx, raw in enumerate(lines, start=1):
        if is_code_fence(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        stripped = raw.strip()
        if not stripped:
            if current_block:
                blocks.append(current_block)
                current_block = []
            continue

        is_heading = bool(re.match(r'^\s*#{1,6}\s', raw))
        is_bullet = bool(re.match(r'^\s*([-*+]|\d+[.)])\s', raw))
        clean = strip_markup(raw).strip()
        clean = re.sub(r'^\s*(\d+[.)])\s*', '', clean).strip()
        if not clean:
            continue

        for sent in split_sentences(clean):
            entry = {
                "line": idx,
                "text": sent,
                "words": words(sent),
                "is_heading": is_heading,
                "is_bullet": is_bullet,
            }
            sentences.append(entry)
            current_block.append(entry)

    if current_block:
        blocks.append(current_block)

    return blocks, sentences


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def add(findings, rule, line, snippet, detail, severity="error"):
    findings.append({
        "rule": rule,
        "line": line,
        "snippet": snippet[:110],
        "detail": detail,
        "severity": severity,
    })


def check_length(sentences, cfg, findings):
    for s in sentences:
        n = len(s["words"])
        cap = HEADLINE_MAX if s["is_heading"] else cfg["sentence_max"]
        label = "headline" if s["is_heading"] else "sentence"
        if n > cap:
            add(findings, "4.1 sentence length", s["line"], s["text"],
                f"{n} words in a {label}; cap is {cap}. Split it.")


def check_paragraphs(blocks, cfg, findings):
    for block in blocks:
        prose = [s for s in block if not s["is_heading"] and not s["is_bullet"]]
        if len(prose) > cfg["para_max"]:
            add(findings, "6.2 paragraph length", prose[0]["line"], prose[0]["text"],
                f"{len(prose)} sentences in one paragraph; cap is {cfg['para_max']}.")


def check_one_idea(sentences, findings):
    for s in sentences:
        if ";" in s["text"]:
            add(findings, "4.2 one idea per sentence", s["line"], s["text"],
                "Semicolon joins two thoughts. Use a period.")
        low = s["text"].lower()
        if len(s["words"]) > 14 and re.search(r',\s+(and|but)\s', low):
            add(findings, "4.2 one idea per sentence", s["line"], s["text"],
                "Comma + conjunction in a long sentence. Probably two sentences.",
                severity="warn")


def check_verbs(sentences, findings):
    for s in sentences:
        toks = [w.lower() for w in s["words"]]

        # -ing forms
        for w in toks:
            if (w.endswith("ing") and len(w) > 4
                    and "-" not in w and w not in ING_ALLOWLIST):
                add(findings, "3.4 no -ing form", s["line"], s["text"],
                    f"'{w}' — use the simple verb, or split the sentence.")

        # passive voice
        for i, w in enumerate(toks):
            if w in BE_FORMS:
                for j in range(i + 1, min(i + 4, len(toks))):
                    cand = toks[j]
                    if cand in ("not", "also", "now", "then", "always", "never"):
                        continue
                    if (cand.endswith("ed") and len(cand) > 3) or cand in IRREGULAR_PARTICIPLES:
                        add(findings, "3.2 active voice", s["line"], s["text"],
                            f"Passive: '{w} {cand}'. Name the actor and put it first.")
                    break

        # perfect / continuous tense
        for i, w in enumerate(toks[:-1]):
            if w in PERFECT_MARKERS:
                nxt = toks[i + 1]
                if (nxt.endswith("ed") and len(nxt) > 3) or nxt in IRREGULAR_PARTICIPLES or nxt == "been":
                    add(findings, "3.5 simple tenses only", s["line"], s["text"],
                        f"Perfect tense: '{w} {nxt}'. Use simple past or present.")
                    break


def check_noun_clusters(sentences, findings):
    for s in sentences:
        run = []
        for w in s["words"]:
            lw = w.lower()
            if lw in FUNCTION_WORDS or lw.endswith("ly"):
                if len(run) >= 4:
                    add(findings, "2.1 noun cluster", s["line"], s["text"],
                        f"Possible noun stack: '{' '.join(run)}'. Max 3 nouns in a row.",
                        severity="warn")
                run = []
            else:
                run.append(w)
        if len(run) >= 4:
            add(findings, "2.1 noun cluster", s["line"], s["text"],
                f"Possible noun stack: '{' '.join(run)}'. Max 3 nouns in a row.",
                severity="warn")


def check_words(sentences, findings):
    for s in sentences:
        low = s["text"].lower()

        for phrase, repl in MULTIWORD_SWAPS.items():
            if phrase in low:
                add(findings, "1.1 approved words", s["line"], s["text"],
                    f"'{phrase}' -> {repl}")

        for w in s["words"]:
            lw = w.lower()
            if lw in SWAPS:
                add(findings, "1.1 approved words", s["line"], s["text"],
                    f"'{lw}' -> {SWAPS[lw]}")
            if lw in MARKETING_FILLER:
                add(findings, "filler", s["line"], s["text"],
                    f"'{lw}' says nothing. Replace with a number or a named outcome.")


def check_punctuation(sentences, findings):
    for s in sentences:
        if "!" in s["text"]:
            add(findings, "8 punctuation", s["line"], s["text"],
                "Exclamation mark. Remove it.")
        if "…" in s["text"] or "..." in s["text"]:
            add(findings, "8 punctuation", s["line"], s["text"],
                "Ellipsis used for tone. Remove it.", severity="warn")
        if re.search(r'\w/\w', s["text"]) and "http" not in s["text"] and "/" not in "0123456789":
            if not re.search(r'\d/\d', s["text"]):
                add(findings, "8 punctuation", s["line"], s["text"],
                    "Slash between words is ambiguous. Pick one, or write both.",
                    severity="warn")
        if s["text"].count("(") > 0 and len(s["words"]) > 18:
            add(findings, "4.2 one idea per sentence", s["line"], s["text"],
                "Parenthesis in a long sentence. Either it matters, or cut it.",
                severity="warn")


def check_benefit_signal(sentences, mode, findings):
    """Marketing only: does the copy ever land on something human?"""
    if mode != "marketing":
        return
    leads = [s for s in sentences if s["is_heading"]][:6]
    for s in leads:
        toks = {w.lower() for w in s["words"]}
        if not (toks & BENEFIT_SIGNALS):
            add(findings, "benefit lead", s["line"], s["text"],
                "Heading names no outcome for the reader. Run the 'so what' chain.",
                severity="warn")

    all_toks = [w.lower() for s in sentences for w in s["words"]]
    you = sum(1 for w in all_toks if w in ("you", "your", "yours", "yourself"))
    we = sum(1 for w in all_toks if w in ("we", "our", "us", "ours"))
    if we > you:
        add(findings, "benefit lead", 0, "(whole document)",
            f"'we/our' appears {we} times vs 'you/your' {you} times. "
            "The reader is not here for the company.",
            severity="warn")


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def run(text, mode):
    cfg = MODES[mode]
    blocks, sentences = parse(text)
    findings = []
    check_length(sentences, cfg, findings)
    check_paragraphs(blocks, cfg, findings)
    check_one_idea(sentences, findings)
    check_verbs(sentences, findings)
    check_noun_clusters(sentences, findings)
    check_words(sentences, findings)
    check_punctuation(sentences, findings)
    check_benefit_signal(sentences, mode, findings)

    findings.sort(key=lambda f: (f["line"], f["rule"]))
    word_total = sum(len(s["words"]) for s in sentences)
    stats = {
        "mode": mode,
        "sentences": len(sentences),
        "words": word_total,
        "avg_sentence_length": round(word_total / len(sentences), 1) if sentences else 0,
        "errors": sum(1 for f in findings if f["severity"] == "error"),
        "warnings": sum(1 for f in findings if f["severity"] == "warn"),
    }
    return stats, findings


def report(stats, findings):
    out = []
    out.append(f"STE check — mode: {stats['mode']}")
    out.append(f"{stats['sentences']} sentences, {stats['words']} words, "
               f"avg {stats['avg_sentence_length']} words/sentence")
    out.append(f"{stats['errors']} errors, {stats['warnings']} warnings")
    out.append("")

    if not findings:
        out.append("Clean on the mechanical pass. Now check terminology consistency")
        out.append("and whether each block lands on a benefit primitive.")
        return "\n".join(out)

    grouped = defaultdict(list)
    for f in findings:
        grouped[f["rule"]].append(f)

    for rule in sorted(grouped, key=lambda r: -len(grouped[r])):
        items = grouped[rule]
        out.append(f"--- {rule}  ({len(items)})")
        seen = set()
        for f in items:
            key = (f["line"], f["detail"])
            if key in seen:
                continue
            seen.add(key)
            mark = "!" if f["severity"] == "error" else "?"
            out.append(f"  {mark} L{f['line']}: {f['detail']}")
            out.append(f"      > {f['snippet']}")
        out.append("")

    out.append("Mechanical pass only. Still to check by hand:")
    out.append("  - one word per concept, one concept per word, across the whole doc")
    out.append("  - every claim checkable (number, named outcome, thing that stops)")
    out.append("  - each block leads on freedom / peace of mind / time back / power")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="ASD-STE100 + benefit-framing checker")
    ap.add_argument("file", help="file to check, or - for stdin")
    ap.add_argument("--mode", default="descriptive", choices=sorted(MODES))
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if args.file == "-":
        text = sys.stdin.read()
    else:
        with open(args.file, "r", encoding="utf-8") as fh:
            text = fh.read()

    stats, findings = run(text, args.mode)

    if args.json:
        print(json.dumps({"stats": stats, "findings": findings}, indent=2))
    else:
        print(report(stats, findings))

    sys.exit(1 if stats["errors"] else 0)


if __name__ == "__main__":
    main()
