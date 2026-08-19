"""
core/voltage_rails.py
------------------------
Voltage-rail reference knowledge base -- links memory/storage fault types
to the specific power rails a technician should check with a multimeter.

IMPORTANT / HONEST DISCLAIMER:
-------------------------------
The voltage values below are GENERIC / JEDEC-STANDARD reference values for
common memory types (LPDDR3, LPDDR4, eMMC). They are a useful STARTING POINT,
but the EXACT voltage on a specific phone board can differ depending on the
PMIC design and manufacturer. Do NOT treat these as guaranteed-accurate for
every board.

The right way to build real value here:
  1. Use these generic entries as a first reference.
  2. When you (or your brother) confirm REAL measured values on a specific
     board/chipset (from a datasheet or actual multimeter reading), add a
     new entry to BOARD_SPECIFIC_OVERRIDES below with that exact model.
  3. Over time, BOARD_SPECIFIC_OVERRIDES becomes your own verified
     knowledge base -- far more reliable than generic values alone.
"""

GENERIC_VOLTAGE_RAILS = {
    "LPDDR4": {
        "description": "LPDDR4 / LPDDR4X RAM (common in mid-range to flagship phones)",
        "rails": [
            {
                "rail_name": "VDD1",
                "typical_voltage": "1.8V",
                "purpose": "I/O supply for periphery logic",
                "measurement_hint": "Measure at the RAM/PMIC-side decoupling capacitor near the RAM chip.",
            },
            {
                "rail_name": "VDD2",
                "typical_voltage": "1.1V",
                "purpose": "Core power supply for the RAM die",
                "measurement_hint": "Often the most critical rail -- missing VDD2 commonly causes "
                                     "'memory device not detected' errors.",
            },
            {
                "rail_name": "VDDQ",
                "typical_voltage": "0.6V",
                "purpose": "I/O supply for the DQ (data) lines",
                "measurement_hint": "Usually derived from VDD2 through an internal/external regulator.",
            },
            {
                "rail_name": "VREF / ZQ",
                "typical_voltage": "0.5 x VDDQ (approx.)",
                "purpose": "Reference voltage for signal calibration",
                "measurement_hint": "Should track proportionally with VDDQ.",
            },
        ],
    },
    "LPDDR3": {
        "description": "LPDDR3 RAM (common in older/budget phones)",
        "rails": [
            {
                "rail_name": "VDD1",
                "typical_voltage": "1.8V",
                "purpose": "I/O supply",
                "measurement_hint": "Measure near RAM chip decoupling capacitors.",
            },
            {
                "rail_name": "VDD2",
                "typical_voltage": "1.2V",
                "purpose": "Core supply",
                "measurement_hint": "Critical rail for RAM core operation.",
            },
            {
                "rail_name": "VDDCA",
                "typical_voltage": "1.2V",
                "purpose": "Command/Address input supply",
                "measurement_hint": "Usually shares the same rail as VDD2 on most designs.",
            },
        ],
    },
    "eMMC": {
        "description": "eMMC storage (common across most mid-range/budget phones)",
        "rails": [
            {
                "rail_name": "VCC",
                "typical_voltage": "2.7V - 3.6V (commonly 2.9V or 3.3V)",
                "purpose": "Main power supply for the eMMC chip",
                "measurement_hint": "Measure directly on the eMMC chip's VCC pins/pads.",
            },
            {
                "rail_name": "VCCQ",
                "typical_voltage": "1.8V (or 3.3V on older designs)",
                "purpose": "I/O supply for eMMC signal lines",
                "measurement_hint": "Missing VCCQ often causes eMMC to be undetected entirely.",
            },
        ],
    },
    "UFS": {
        "description": "UFS storage (common in flagship/newer phones)",
        "rails": [
            {
                "rail_name": "VCC",
                "typical_voltage": "2.7V - 3.6V (commonly 2.9V)",
                "purpose": "Main power supply",
                "measurement_hint": "Measure directly on the UFS chip's VCC pins/pads.",
            },
            {
                "rail_name": "VCCQ",
                "typical_voltage": "1.2V or 1.8V (design-dependent)",
                "purpose": "I/O supply",
                "measurement_hint": "Check chip datasheet -- UFS I/O voltage varies more than eMMC.",
            },
            {
                "rail_name": "VCCQ2",
                "typical_voltage": "1.8V",
                "purpose": "Secondary I/O supply (on some UFS designs)",
                "measurement_hint": "Not present on all UFS chips -- verify against datasheet.",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Board/chipset-SPECIFIC verified values -- start empty.
# This is where real, confirmed measurements go as you and your brother
# test actual boards. Format:
#
#   "Phone Model or Chipset Name": {
#       "memory_type": "LPDDR4",             # which generic table it relates to
#       "verified_rails": {
#           "VDD2": "1.125V",                # actual measured/confirmed value
#       },
#       "notes": "Confirmed via multimeter on <date> by <technician>",
#   }
# ---------------------------------------------------------------------------
BOARD_SPECIFIC_OVERRIDES = {
    # Example placeholder -- replace/add real entries as you confirm them:
    # "Redmi Note 10 (MT6768)": {
    #     "memory_type": "LPDDR4",
    #     "verified_rails": {"VDD2": "1.125V"},
    #     "notes": "Confirmed via multimeter, 2026-08-20, by Riaz's brother.",
    # },
}


# ---------------------------------------------------------------------------
# Which fault keywords/categories should trigger a voltage-rail checklist
# ---------------------------------------------------------------------------
FAULT_TO_MEMORY_TYPE = {
    "mmc0: error": "eMMC",
    "emmc init fail": "eMMC",
    "ufs init fail": "UFS",
    "no_memory_device_detected": "LPDDR4",
    "ddr_abort": "LPDDR4",
    "dram": "LPDDR4",
    "lpddr": "LPDDR4",
}


def get_voltage_checklist(log_text, phone_model=""):
    """
    Log text mein memory/storage-related fault keyword mile, to us
    memory-type ka voltage-rail checklist return karta hai.
    """
    lower_log = log_text.lower()
    matched_types = set()

    for keyword, mem_type in FAULT_TO_MEMORY_TYPE.items():
        if keyword.lower() in lower_log:
            matched_types.add(mem_type)

    if not matched_types:
        return []

    results = []
    for mem_type in matched_types:
        entry = GENERIC_VOLTAGE_RAILS.get(mem_type)
        if not entry:
            continue

        verified_override = None
        for board_name, override_data in BOARD_SPECIFIC_OVERRIDES.items():
            if (phone_model and phone_model.lower() in board_name.lower()
                    and override_data["memory_type"] == mem_type):
                verified_override = override_data
                break

        results.append({
            "memory_type": mem_type,
            "description": entry["description"],
            "rails": entry["rails"],
            "verified_override": verified_override,
        })

    return results


def format_voltage_checklist(checklist):
    """checklist ko readable text mein convert karta hai, UI mein dikhane ke liye."""
    if not checklist:
        return ""

    lines = ["\n" + "=" * 50, "VOLTAGE-RAIL CHECKLIST (measure with multimeter)", "=" * 50]

    for entry in checklist:
        lines.append(f"\n[{entry['memory_type']}] {entry['description']}")

        if entry["verified_override"]:
            lines.append("  ** VERIFIED values for this board found: **")
            for rail, voltage in entry["verified_override"]["verified_rails"].items():
                lines.append(f"     {rail}: {voltage}  (confirmed)")
            lines.append(f"     Note: {entry['verified_override']['notes']}")

        lines.append("  Generic reference rails (verify against actual datasheet):")
        for rail in entry["rails"]:
            lines.append(f"     {rail['rail_name']}: ~{rail['typical_voltage']}"
                          f" -- {rail['purpose']}")
            lines.append(f"        Hint: {rail['measurement_hint']}")

    lines.append("\nReminder: Generic values are typical/industry-standard references, "
                 "NOT guaranteed for every board. Always cross-check with the specific "
                 "chip's datasheet or schematic before concluding a rail is faulty.")

    return "\n".join(lines)