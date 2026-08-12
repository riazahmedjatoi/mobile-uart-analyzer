FAULT_PATTERNS = [
    # --- Storage (eMMC / UFS) related ---
    {
        "keyword": "mmc0: error",
        "category": "Storage (eMMC)",
        "hint": "eMMC storage chip se error aa raha hai. Chip damage, "
                "dry solder joint, ya corrupted storage ho sakta hai.",
    },
    {
        "keyword": "emmc init fail",
        "category": "Storage (eMMC)",
        "hint": "eMMC initialize hi nahi ho paya. Reball/replace check karo.",
    },
    {
        "keyword": "ufs init fail",
        "category": "Storage (UFS)",
        "hint": "UFS storage chip initialize nahi hua -- naye phones mein "
                "eMMC ki jagah UFS use hoti hai, isi tarah ka issue.",
    },

    # --- Power / PMIC related ---
    {
        "keyword": "pwrap",
        "category": "Power (PMIC)",
        "hint": "PMIC (Power Management IC) se related logs. Agar yahan "
                "ruk jaye ya error aaye, to power IC ya power rail check karo.",
    },
    {
        "keyword": "pmic",
        "category": "Power (PMIC)",
        "hint": "PMIC chip ka zikr aa raha hai -- power sequence dekh kar "
                "confirm karo sab steps 'ok' status ke saath complete hue ya nahi.",
    },
    {
        "keyword": "power sequence fail",
        "category": "Power (PMIC)",
        "hint": "Power-on sequence beech mein fail ho gaya -- PMIC ya "
                "power rail (voltage regulator) ka issue ho sakta hai.",
    },

    # --- Bootloader / Preloader related ---
    {
        "keyword": "preloader",
        "category": "Bootloader",
        "hint": "Preloader stage ka log -- ye pehla software step hota hai "
                "jo storage chip se load hota hai.",
    },
    {
        "keyword": "bootloader",
        "category": "Bootloader",
        "hint": "Bootloader se related activity -- corrupt ho sakta hai "
                "agar aage boot na badhe.",
    },
    {
        "keyword": "fastboot",
        "category": "Bootloader",
        "hint": "Phone fastboot mode mein ja raha hai -- normal boot fail "
                "hone ki nishaani ho sakti hai.",
    },
    {
        "keyword": "dm-verity",
        "category": "Bootloader / Security",
        "hint": "Verified boot check fail ho raha hai -- partition "
                "corruption ya modification ki wajah se ho sakta hai.",
    },

    # --- CPU / Boot loop ---
    {
        "keyword": "watchdog",
        "category": "CPU / Boot Loop",
        "hint": "Watchdog timer trigger hua -- system hang ho kar restart "
                "hua. Baar baar aana boot-loop ka sign hai.",
    },
    {
        "keyword": "reboot reason",
        "category": "CPU / Boot Loop",
        "hint": "Phone restart hua hai -- iske aage wali line mein reboot "
                "ki wajah (reason) likhi hoti hai.",
    },

    # --- Connectivity / RF ---
    {
        "keyword": "modem",
        "category": "Signal / Communication",
        "hint": "Modem/baseband se related log -- network/signal issues "
                "ke liye is section ko dhyan se dekho.",
    },
    {
        "keyword": "rf cal",
        "category": "Signal / Communication",
        "hint": "RF calibration data se related -- signal problems ka "
                "clue mil sakta hai.",
    },
]


def get_all_categories():
    """Saari unique categories ki list deta hai (UI filter ke liye useful)."""
    return sorted(set(p["category"] for p in FAULT_PATTERNS))
