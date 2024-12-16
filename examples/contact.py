import badger2040
import qrcode
import time
import os
import badger_os

# Check that the qrcodes directory exists, if not, make it
try:
    os.mkdir("/qrcodes")
except OSError:
    pass

# Check that there is a qrcode.txt, if not preload
try:
    text = open("/qrcodes/contact.txt", "r")
except OSError:
    text = open("/qrcodes/contact.txt", "w")
    if badger2040.is_wireless():
        text.write("""https://pimoroni.com/badger2040w
Badger 2040 W
* 296x128 1-bit e-ink
* 2.4GHz wireless & RTC
* five user buttons
* user LED
* 2MB QSPI flash

Scan this code to learn
more about Badger 2040 W.
""")
    else:
        text.write("""https://pimoroni.com/badger2040
Badger 2040
* 296x128 1-bit e-ink
* five user buttons
* user LED
* 2MB QSPI flash

Scan this code to learn
more about Badger 2040.
""")
    text.flush()
    text.seek(0)

# Load all available QR Code Files
try:
    CODES = [f for f in os.listdir("/qrcodes") if f.endswith(".txt")]
    TOTAL_CODES = len(CODES)
except OSError:
    pass


print(f'There are {TOTAL_CODES} QR Codes available:')
for codename in CODES:
    print(f'File: {codename}')

display = badger2040.Badger2040()

code = qrcode.QRCode()

state = {
    "current_qr": 0
}


def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    display.set_pen(15)
    display.rectangle(ox, oy, size, size)
    display.set_pen(0)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)


def draw_qr_file(n):
    display.led(128)
    file = CODES[n]
    codetext = open("/qrcodes/{}".format(file), "r")

    lines = codetext.read().strip().split("\n")
    code_text = lines.pop(0)
    title_text = lines.pop(0)
    detail_text = lines

    # Clear the Display
    display.set_pen(15)  # Change this to 0 if a white background is used
    display.clear()
    display.set_pen(0)

    code.set_text(code_text)
    size, _ = measure_qr_code(128, code)
    left = top = int((badger2040.HEIGHT / 2) - (size / 2))
    draw_qr_code(left, top, 128, code)

    left = 128 + 5

    display.set_font("bitmap6")
    display.text(title_text, left, 20, badger2040.WIDTH, 2)

    top = 40
    for line in detail_text:
        if "Scan" in line or "Badger" in title_text:
            display.set_font("bitmap6")
            display.text(line, left, top, badger2040.WIDTH, 1)
        else:
            display.set_font("sans")
            display.text(line, left, top, badger2040.WIDTH, 0.55)
        if "Badger" in title_text:
            top += 10
        else:
            top += 15

    if TOTAL_CODES > 1:
        for i in range(TOTAL_CODES):
            x = 286
            y = int((128 / 2) - (TOTAL_CODES * 10 / 2) + (i * 10))
            display.set_pen(0)
            display.rectangle(x, y, 8, 8)
            if state["current_qr"] != i:
                display.set_pen(15)
                display.rectangle(x + 1, y + 1, 6, 6)
    display.update()


badger_os.state_load("qrcodes", state)
changed = True

while True:
    # Sometimes a button press or hold will keep the system
    # powered *through* HALT, so latch the power back on.
    display.keepalive()

    if TOTAL_CODES > 1:
        if display.pressed(badger2040.BUTTON_UP):
            if state["current_qr"] > 0:
                state["current_qr"] -= 1
                changed = True

        if display.pressed(badger2040.BUTTON_DOWN):
            if state["current_qr"] < TOTAL_CODES - 1:
                state["current_qr"] += 1
                changed = True

    if display.pressed(badger2040.BUTTON_B) or display.pressed(badger2040.BUTTON_C):
        display.set_pen(15)
        display.clear()
        badger_os.warning(display, "To add QR codes, connect Badger 2040 W to a PC, load up Thonny, and add files to /qrcodes directory.")
        time.sleep(4)
        changed = True

    if changed:
        draw_qr_file(state["current_qr"])
        badger_os.state_save("qrcodes", state)
        changed = False

    # Halt the Badger to save power, it will wake up if any of the front buttons are pressed
    display.halt()
