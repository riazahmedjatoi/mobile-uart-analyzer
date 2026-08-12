from .fault_patterns import FAULT_PATTERNS
from .boot_loop_detector import detect_boot_loop, format_boot_loop_result


def run_local_analysis(log_text):
    """
    Do cheezein karta hai:
      1. Known keywords dhoondta hai (fault_patterns.py se) -- fixed signatures.
      2. Algorithmic boot-loop detection chalata hai (boot_loop_detector.py) --
         ye kisi keyword pe depend nahi karta, khud repeating patterns dhoondta hai.

    Return: list of dicts, har match ke liye:
        {
            "keyword": "...",
            "category": "...",
            "hint": "...",
            "matched_lines": [line1, line2, ...],   # jin lines mein mila
        }
    Agar kuch na mile to empty list.
    """
    results = []
    lower_log = log_text.lower()
    log_lines = log_text.splitlines()

    for pattern in FAULT_PATTERNS:
        keyword = pattern["keyword"].lower()
        if keyword in lower_log:
            matched_lines = [ln for ln in log_lines if keyword in ln.lower()]
            results.append({
                "keyword": pattern["keyword"],
                "category": pattern["category"],
                "hint": pattern["hint"],
                "matched_lines": matched_lines[:5],  # zyada se zyada 5 lines dikhao
            })

    # --- Algorithmic boot-loop detection (keyword-independent) ---
    loop_result = detect_boot_loop(log_text)
    if loop_result:
        results.append({
            "keyword": "(auto-detected repeating pattern)",
            "category": f"CPU / Boot Loop [{loop_result['confidence']} confidence]",
            "hint": (
                f"{loop_result['block_size']}-line block "
                f"{loop_result['repeats']}x repeat hua -- yaani chip kisi stage "
                f"pe atak kar baar-baar restart ho rahi hai. Ye keyword-match nahi "
                f"hai, khud pattern se detect hua hai."
            ),
            "matched_lines": loop_result["block_lines"],
        })

    return results


def format_local_analysis_summary(results):
    """
    run_local_analysis() ka output ek readable text mein convert karta hai,
    UI mein dikhane ke liye.
    """
    if not results:
        return ("Koi known fault-pattern match nahi hua. Iska matlab ye nahi "
                "ki phone theek hai -- ho sakta hai fault UART log mein "
                "dikhta hi na ho. Neeche 'Copy for AI' button se poora log "
                "kisi AI ko de kar detailed analysis karwao.")

    lines = ["Local Quick-Check Results:\n"]
    for r in results:
        lines.append(f"[{r['category']}] Keyword: '{r['keyword']}'")
        lines.append(f"  -> {r['hint']}")
        lines.append(f"  Matched lines ({len(r['matched_lines'])} shown):")
        for ml in r["matched_lines"]:
            lines.append(f"     {ml}")
        lines.append("")

    return "\n".join(lines)


def build_ai_prompt(log_text, phone_model="", local_findings=None):
    """
    Log ko ek structured prompt mein wrap karta hai jo technician kisi bhi
    LLM ko copy-paste kar sakta hai.

    local_findings: run_local_analysis() ka output, optional -- agar diya
    jaye to prompt mein "already detected hints" bhi include ho jayenge,
    jisse AI ka response aur bhi accurate ho sakta hai.
    """
    model_line = f"Phone Model: {phone_model}\n" if phone_model else ""

    hints_section = ""
    if local_findings:
        hint_lines = [f"- {f['category']}: {f['hint']}" for f in local_findings]
        hints_section = (
            "\nLocal keyword-scan ne ye possible clues diye hain "
            "(inhe confirm/reject karo apne analysis mein):\n"
            + "\n".join(hint_lines) + "\n"
        )

    prompt = f"""You are an expert mobile phone hardware and semiconductor diagnostic engineer.

{model_line}Below is a live UART boot log captured from a mobile phone motherboard:

```text
{log_text}
```
{hints_section}
Please analyze this log and answer clearly:

1. Boot Status: Kaha tak boot process successfully complete hua, aur kaha atka/fail hua?
2. Detected Fault: Hardware ya software issue kya lag raha hai? (eMMC/UFS Failure, PMIC Fault, Preloader Corruption, Boot Loop, ya kuch aur)
3. Confidence Level: Ye analysis kitna certain hai (High / Medium / Low) is log ke basis par?
4. Suggested Repair Steps: Ek mobile repair technician ko agla practical step kya lena chahiye?
"""
    return prompt