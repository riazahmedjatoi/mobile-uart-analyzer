"""
core/qualcomm_sbl_parser.py
-----------------------------
Parser for Qualcomm's SBL (Secondary Boot Loader) log format.

WHY THIS IS DIFFERENT FROM fault_patterns.py:
------------------------------------------------
fault_patterns.py does simple keyword guessing ("this text appeared,
might mean X"). This module instead reads the ACTUAL STRUCTURE of
Qualcomm's own bootloader log format, which is publicly documented as:

    Log Type - Time(microseconds) - Message
    B = Since Boot (a stage STARTED)
    D = Delta (a stage COMPLETED, with duration)
    S = Static info (chip/board identifiers)

Every stage that starts ("B - ... , Start") is expected to be followed,
later in the log, by a matching completion line ("D - ... , Delta").

KEY INSIGHT (verified against real Qualcomm engineering bug reports,
including Qualcomm's own public GitHub issue tracker):
    If a stage STARTS but never gets its matching "Delta" (completion)
    line, that is exactly the stage where the boot process hung or
    crashed. This is not a guess -- it's the firmware itself reporting
    where it stopped.

Additionally, Qualcomm SBL logs report explicit crash points in the
format:
    "Error code <hex> at <source_file>.c Line <number>"
This module extracts that too, and maps the source file name to a
likely subsystem (DDR / Storage / PMIC / Secure Boot / etc.) based on
well-known Qualcomm source file naming conventions.

LIMITATION (being upfront): This only applies to Qualcomm-platform
boot logs. MediaTek and other chipsets use a different log format
entirely -- this module will simply find nothing and return an empty
result on those logs, which is the correct/safe behavior.

ANOTHER LIMITATION: the source-file-to-subsystem mapping tells you
WHERE the code crashed, not necessarily the ROOT CAUSE. A crash inside
a storage-related file can sometimes be triggered by an upstream PMIC
failure. Always confirm with a multimeter/schematic before concluding
a specific rail or part is faulty.
"""

import re

STAGE_LINE_RE = re.compile(r"^\s*([BDS])\s*-\s*(\d+)\s*-\s*(.+?)\s*$")
ERROR_LINE_RE = re.compile(
    r"Error code\s+([0-9a-fA-F]+)\s+at\s+([\w./\\-]+\.c)\s+Line\s+(\d+)",
    re.IGNORECASE,
)

# Known Qualcomm source-file naming patterns -> likely subsystem.
# This is based on publicly visible Qualcomm boot-source file names
# (e.g. ddr_external_api.c, boot_block_dev.c, boot_elf_loader.c seen in
# real bug reports / forums), NOT internal/confidential information.
SUBSYSTEM_FILE_HINTS = [
    (["ddr", "sdram", "dram"], "DDR / RAM"),
    (["block_dev", "emmc", "mmc", "ufs", "storage", "flash"], "Storage (eMMC/UFS)"),
    (["pm_", "pmic", "spmi", "regulator", "power"], "PMIC / Power"),
    (["elf_loader", "secboot", "auth", "hash_seg"], "Secure Boot / Image Verification"),
    (["usb"], "USB"),
    (["clock", "clk"], "Clock Initialization"),
]


def _guess_subsystem(source_file):
    lower = source_file.lower()
    for keywords, subsystem in SUBSYSTEM_FILE_HINTS:
        if any(kw in lower for kw in keywords):
            return subsystem
    return "Unknown subsystem (check file name manually)"


def is_qualcomm_sbl_log(log_text):
    """
    Quick check: does this log look like Qualcomm's SBL format at all?
    (Looks for the 'B - <number> - ' pattern appearing multiple times.)
    Returns False for MediaTek/other logs -- so this parser safely does
    nothing on non-Qualcomm logs.
    """
    matches = 0
    for line in log_text.splitlines():
        if STAGE_LINE_RE.match(line):
            matches += 1
            if matches >= 3:
                return True
    return False


def parse_qualcomm_sbl_log(log_text):
    """
    Returns None if this doesn't look like a Qualcomm SBL log.
    Otherwise returns a dict:
        {
            "stuck_stage": "pm_device_init" or None,   # stage that started
                                                          # but never completed
            "error_codes": [
                {"code": "84", "source_file": "ddr_external_api.c",
                 "line": "417", "subsystem": "DDR / RAM"},
                ...
            ],
        }
    """
    if not is_qualcomm_sbl_log(log_text):
        return None

    started_stages = []   # list of stage names, in order
    completed_stages = set()
    error_codes = []

    for line in log_text.splitlines():
        stage_match = STAGE_LINE_RE.match(line)
        if stage_match:
            log_type, _timestamp, message = stage_match.groups()

            if log_type == "B" and message.endswith(", Start"):
                stage_name = message[: -len(", Start")].strip()
                started_stages.append(stage_name)
            elif log_type == "D" and message.endswith(", Delta"):
                stage_name = message[: -len(", Delta")].strip()
                completed_stages.add(stage_name)

        error_match = ERROR_LINE_RE.search(line)
        if error_match:
            code, source_file, line_no = error_match.groups()
            # Only keep the filename, not the full compile-time path
            short_file = source_file.replace("\\", "/").split("/")[-1]
            error_codes.append({
                "code": code,
                "source_file": short_file,
                "line": line_no,
                "subsystem": _guess_subsystem(short_file),
            })

    # Find the LAST stage that started but never got a matching Delta --
    # that's the stage the boot process was in when it stopped.
    stuck_stage = None
    for stage_name in reversed(started_stages):
        if stage_name not in completed_stages:
            stuck_stage = stage_name
            break

    return {
        "stuck_stage": stuck_stage,
        "error_codes": error_codes,
    }


def format_qualcomm_sbl_result(result):
    """Converts parse_qualcomm_sbl_log() output into readable text."""
    if not result:
        return ""

    if not result["stuck_stage"] and not result["error_codes"]:
        return ""

    lines = ["\n" + "=" * 50, "QUALCOMM SBL LOG ANALYSIS (parsed from firmware's own log structure)", "=" * 50]

    if result["stuck_stage"]:
        lines.append(
            f"\nBoot got stuck during stage: '{result['stuck_stage']}'"
        )
        lines.append(
            "  -> This stage started ('B - ... Start') but never reported "
            "completion ('D - ... Delta') anywhere later in the log. This "
            "is the firmware itself indicating where the boot process "
            "stopped -- not a keyword guess."
        )

    if result["error_codes"]:
        lines.append("\nExplicit error code(s) reported by firmware:")
        for err in result["error_codes"]:
            lines.append(
                f"  Error code {err['code']} at {err['source_file']} "
                f"(Line {err['line']})"
            )
            lines.append(f"     Likely subsystem: {err['subsystem']}")

    lines.append(
        "\nNote: subsystem mapping is based on Qualcomm's typical source-file "
        "naming conventions. It tells you WHICH subsystem to investigate, "
        "not the exact component/voltage -- confirm with a multimeter or "
        "schematic before concluding a specific rail/part is faulty."
    )

    return "\n".join(lines)