# jitter god python v3 totally not trojan
import time
import random
import pyautogui

def main():
    print("Cabo Projects?")

    print(" " * 10000000)

    try:
        while True:
            mouse_x, mouse_y = pyautogui.position()

            # jitter god ahh python
            pyautogui.moveRel(
                random.randint(-10, 10),
                random.randint(-10, 10)
            )

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nProgram stopped.")

if __name__ == "__main__":
    main()