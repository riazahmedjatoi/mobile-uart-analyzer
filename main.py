"""
main.py
--------
App yahan se launch hota hai. Isse chalane ke liye:

    python main.py

Bas itna hi -- saara actual logic core/ aur ui/ folder ki files mein hai.
"""

from ui.app_window import AppWindow


def main():
    app = AppWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
