"""
core/boot_loop_detector.py
----------------------------
Algorithmic boot-loop detection -- kisi fixed keyword pe depend nahi karta.

Idea: Agar phone boot loop mein phasa hai, to UART log mein ek hi group of
lines baar-baar (identical) repeat hoti hai -- jaise chip kisi stage pe
atak kar restart ho rahi hai, aur wahi initialization sequence dobara chal
rahi hai.

Algorithm (sliding window + hashing):
  1. Log ko lines mein todo, khaali/trivial lines clean karo.
  2. Alag-alag block-sizes (3 se MAX_BLOCK_SIZE lines tak) try karo.
  3. Har block-size ke liye, saare possible consecutive-line blocks ka
     "signature" (tuple of lines) banao aur dictionary mein count karo.
  4. Jo block sabse zyada baar (>= MIN_REPEATS) aur sabse bada (informative)
     repeat hota hai, use best match maan lo.
  5. Trivial blocks (sirf blank lines, ya bahut chhoti lines, ya sirf ek hi
     subsystem/tag se bana hua chhota block) ko ignore karo taaki
     false-positives na aayen.

Ye function GUI se independent hai, isliye standalone bhi test ho sakta hai.
"""

MIN_BLOCK_SIZE = 3
MAX_BLOCK_SIZE = 15
MIN_REPEATS = 2
MIN_MEANINGFUL_LINE_LENGTH = 4  # isse chhoti lines "trivial" maani jayengi


def _clean_lines(log_text):
    """Blank aur bohot chhoti (noise) lines hata kar saaf list deta hai,
    lekin original line content preserve karta hai."""
    lines = [ln.strip() for ln in log_text.splitlines()]
    return [ln for ln in lines if len(ln) >= MIN_MEANINGFUL_LINE_LENGTH]


def _extract_tag(line):
    """
    Line ka 'source tag' nikaalta hai -- jaise '[RTC] get_freq...' se '[RTC]',
    ya 'Pll init start...' se 'Pll'. Isse hum check kar sakte hain ki ek
    repeating block mein kitne ALAG subsystems shaamil hain.
    """
    line = line.strip()
    if line.startswith("["):
        end = line.find("]")
        if end != -1:
            return line[:end + 1]
    return line.split()[0] if line.split() else ""


def _is_trivial_block(block):
    """
    Ek block ko 'trivial' (false-positive) maanne ke do cases:

    1. Saari lines hi bilkul same hain aur choti hain (jaise sirf '....').
    2. Poora block SIRF EK HI subsystem/tag se hai (jaise sirf baar-baar
       [RTC] ki readings) -- ye normal ek-baar-hone-wali calibration/polling
       routine hoti hai, asli reboot-loop nahi. Asli boot-loop mein alag-alag
       subsystems (PLL, MUX, PWRAP, etc.) ek sath restart hote hain, isliye
       tags mein diversity honi chahiye jab tak block bada na ho.
    """
    unique_lines = set(block)
    if len(unique_lines) == 1:
        return len(block[0]) < 10

    tags = {_extract_tag(ln) for ln in block}
    if len(tags) <= 1 and len(block) < 6:
        # Sirf ek hi tag/module, aur block bhi zyada bada nahi -- likely
        # normal repeated polling/measurement hai, boot-loop nahi.
        return True

    return False


def detect_boot_loop(log_text):
    """
    Return: dict agar boot-loop pattern mila, warna None.

    Dict format:
        {
            "detected": True,
            "block_size": 5,          # kitni lines ka repeating group hai
            "repeats": 3,              # kitni baar repeat hua
            "confidence": "High",       # High / Medium, block_size aur repeats par based
            "block_lines": [...],        # repeating group ki actual lines
        }
    """
    lines = _clean_lines(log_text)
    n = len(lines)
    if n < MIN_BLOCK_SIZE * MIN_REPEATS:
        return None  # log itna chhota hai ki loop detect karna meaningful nahi

    best = None

    for block_size in range(MIN_BLOCK_SIZE, min(MAX_BLOCK_SIZE, n // MIN_REPEATS) + 1):
        seen_positions = {}

        for i in range(n - block_size + 1):
            block = tuple(lines[i:i + block_size])
            if _is_trivial_block(block):
                continue
            seen_positions.setdefault(block, []).append(i)

        for block, positions in seen_positions.items():
            if len(positions) < MIN_REPEATS:
                continue

            # Non-overlapping occurrences hi count karo (real repeats)
            non_overlapping = [positions[0]]
            for pos in positions[1:]:
                if pos >= non_overlapping[-1] + block_size:
                    non_overlapping.append(pos)

            repeats = len(non_overlapping)
            if repeats < MIN_REPEATS:
                continue

            score = block_size * repeats  # bada block + zyada repeats = zyada confident
            if best is None or score > best["score"]:
                best = {
                    "block": block,
                    "block_size": block_size,
                    "repeats": repeats,
                    "score": score,
                }

    if best is None:
        return None

    # Confidence label -- simple heuristic
    if best["repeats"] >= 3 and best["block_size"] >= 4:
        confidence = "High"
    else:
        confidence = "Medium"

    return {
        "detected": True,
        "block_size": best["block_size"],
        "repeats": best["repeats"],
        "confidence": confidence,
        "block_lines": list(best["block"]),
    }


def format_boot_loop_result(result):
    """detect_boot_loop() ka output ek readable text mein convert karta hai."""
    if not result:
        return None

    lines = [
        f"[CPU / Boot Loop - Auto-Detected Pattern] Confidence: {result['confidence']}",
        f"  -> Ek {result['block_size']}-line ka group {result['repeats']} baar "
        f"repeat hua hai -- ye classic boot-loop signature hai (chip kisi stage "
        f"pe atak kar baar-baar restart ho rahi hai).",
        "  Repeating block:",
    ]
    for ln in result["block_lines"]:
        lines.append(f"     {ln}")

    return "\n".join(lines)