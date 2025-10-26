from flask import Flask, request, render_template
import os
import datetime

app = Flask(__name__)

# === NASTAVENIA ===
HISTORY = True  # Zmeň na False, ak nechceš ukladať históriu

if HISTORY:
    os.makedirs('history', exist_ok=True)

# === SK QWERTY LAYOUT pre RAW HID ===
SK_KEYMAP = {
    # Základné písmená
    'a': (0, 4), 'b': (0, 5), 'c': (0, 6), 'd': (0, 7), 'e': (0, 8), 'f': (0, 9),
    'g': (0, 10), 'h': (0, 11), 'i': (0, 12), 'j': (0, 13), 'k': (0, 14), 'l': (0, 15),
    'm': (0, 16), 'n': (0, 17), 'o': (0, 18), 'p': (0, 19), 'q': (0, 20), 'r': (0, 21),
    's': (0, 22), 't': (0, 23), 'u': (0, 24), 'v': (0, 25), 'w': (0, 26), 'x': (0, 27),
    'y': (0, 28), 'z': (0, 29),

    'A': (2, 4), 'B': (2, 5), 'C': (2, 6), 'D': (2, 7), 'E': (2, 8), 'F': (2, 9),
    'G': (2, 10), 'H': (2, 11), 'I': (2, 12), 'J': (2, 13), 'K': (2, 14), 'L': (2, 15),
    'M': (2, 16), 'N': (2, 17), 'O': (2, 18), 'P': (2, 19), 'Q': (2, 20), 'R': (2, 21),
    'S': (2, 22), 'T': (2, 23), 'U': (2, 24), 'V': (2, 25), 'W': (2, 26), 'X': (2, 27),
    'Y': (2, 28), 'Z': (2, 29),

    # Čísla a základ
    '1': (0, 30), '2': (0, 31), '3': (0, 32), '4': (0, 33), '5': (0, 34),
    '6': (0, 35), '7': (0, 36), '8': (0, 37), '9': (0, 38), '0': (0, 39),
    ' ': (0, 44), '\n': (0, 40), '\t': (0, 43),

    # Špeciálne znaky (SK QWERTY)
    '!': (2, 30), '"': (2, 34), '#': (64, 11), '$': (2, 35), '%': (2, 36),
    '&': (2, 37), '\'': (0, 52), '(': (2, 38), ')': (2, 39), '*': (2, 55),
    '+': (64, 27), ',': (0, 54), '-': (0, 45), '.': (0, 55), '/': (0, 56),
    ':': (2, 54), ';': (0, 51), '<': (64, 28), '=': (0, 46), '>': (64, 29),
    '?': (2, 56), '@': (64, 20), '[': (64, 9), '\\': (64, 26), ']': (64, 10),
    '^': (64, 35), '_': (2, 45), '`': (0, 53), '{': (64, 21), '|': (64, 49),
    '}': (64, 22), '~': (64, 53),

    # Diakritika
    'á': (64, 52), 'Á': (66, 52),
    'ä': (64, 9),  'Ä': (66, 9),
    'č': (64, 6),  'Č': (66, 6),
    'ď': (64, 7),  'Ď': (66, 7),
    'é': (64, 8),  'É': (66, 8),
    'í': (64, 12), 'Í': (66, 12),
    'ĺ': (64, 51), 'Ĺ': (66, 51),
    'ľ': (64, 15), 'Ľ': (66, 15),
    'ň': (64, 17), 'Ň': (66, 17),
    'ó': (64, 18), 'Ó': (66, 18),
    'ô': (66, 18), 'Ô': (66, 18),
    'ŕ': (64, 21), 'Ŕ': (66, 21),
    'š': (64, 22), 'Š': (66, 22),
    'ť': (64, 23), 'Ť': (66, 23),
    'ú': (64, 24), 'Ú': (66, 24),
    'ý': (64, 28), 'Ý': (66, 28),
    'ž': (64, 29), 'Ž': (66, 29),
    '€': (64, 8),
}

def get_hid_code(char):
    return SK_KEYMAP.get(char)

def encode_string(text):
    codes = []
    for c in text:
        hid = get_hid_code(c)
        if hid:
            codes.append(hid)
    return codes

def codes_to_array(codes, name):
    arr = []
    for mod, key in codes:
        arr.append(str(mod))
        arr.append(str(key))
    return f"const uint8_t {name}[] PROGMEM = {{{', '.join(arr)}}};"

def parse_ducky_script(script):
    lines = script.splitlines()
    arduino_lines = []
    string_blocks = []
    block_id = 0

    for line in lines:
        line = line.strip()
        if not line or line.startswith('REM'):
            continue
        parts = line.split(maxsplit=1)
        cmd = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else ''

        if cmd == 'STRING':
            codes = encode_string(arg)
            if codes:
                name = f"key_arr_{block_id}"
                string_blocks.append(codes_to_array(codes, name))
                preview = arg[:30].replace('\n', '\\n')
                arduino_lines.append(f"  duckyString({name}, sizeof({name})); // STRING {preview}{'...' if len(arg) > 30 else ''}")
                block_id += 1
        elif cmd == 'DELAY':
            arduino_lines.append(f"  delay({arg}); // DELAY {arg}")
        elif cmd == 'GUI' or cmd == 'WINDOWS':
            if arg.lower() == 'r':
                arduino_lines.append("  keyboard::type(21, 0, 0, 0, 0, 0, 8); // GUI r")
            elif arg.lower() == 'm':
                arduino_lines.append("  keyboard::type(16, 0, 0, 0, 0, 0, 8); // GUI m")
            elif arg in 'abcdefghijklmnopqrstuvwxyz':
                kc = ord(arg) - ord('a') + 4
                arduino_lines.append(f"  keyboard::type({kc}, 0, 0, 0, 0, 0, 8); // GUI {arg}")
        elif cmd == 'ENTER':
            arduino_lines.append("  keyboard::type(40, 0, 0, 0, 0, 0, 0); // ENTER")
        elif cmd == 'TAB':
            arduino_lines.append("  keyboard::type(43, 0, 0, 0, 0, 0, 0); // TAB")
        elif cmd == 'SPACE':
            arduino_lines.append("  keyboard::type(44, 0, 0, 0, 0, 0, 0); // SPACE")
        elif cmd == 'UP':
            arduino_lines.append("  keyboard::type(82, 0, 0, 0, 0, 0, 0); // UP")
        elif cmd == 'DOWN':
            arduino_lines.append("  keyboard::type(81, 0, 0, 0, 0, 0, 0); // DOWN")
        elif cmd == 'LEFT':
            arduino_lines.append("  keyboard::type(80, 0, 0, 0, 0, 0, 0); // LEFT")
        elif cmd == 'RIGHT':
            arduino_lines.append("  keyboard::type(79, 0, 0, 0, 0, 0, 0); // RIGHT")
        elif cmd == 'ALT' and arg.upper() == 'TAB':
            arduino_lines.append("  keyboard::type(43, 0, 0, 0, 0, 0, 4); // ALT TAB")
        else:
            arduino_lines.append(f"  // Nepodporovaný príkaz: {line}")

    return string_blocks, arduino_lines

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_route():
    data = request.get_json()
    script = data.get('script', '').strip()

    # === ULOŽENIE DO HISTÓRIE ===
    if HISTORY and script:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"history/DuckyCode_{timestamp}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(script)
        except Exception as e:
            print(f"[HISTÓRIA] Chyba: {e}")

    # === GENEROVANIE ARDUINO KÓDU ===
    string_blocks, arduino_lines = parse_ducky_script(script)

    full_code = f"""// [ ===== Created using local Duckify SK ===== ] //
// Based on duckify.spacehuhn.com – raw HID for full SK keyboard support
// Platform: Arduino Pro Micro
// Keyboard Layout: SK (QWERTY)

#include <HID.h>

const int buttonPin = 2;   // D2 – tlačidlo medzi D2 a GND
const int greenLed = 13;   // Built-in LED

namespace keyboard {{
    typedef struct report {{
        uint8_t modifiers;
        uint8_t reserved;
        uint8_t keys[6];
    }} report;
    
    report prev_report = report {{ 0x00, 0x00, {{ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }} }};
    
    const uint8_t keyboardDescriptor[] PROGMEM {{
        0x05, 0x01, 0x09, 0x06, 0xa1, 0x01, 0x85, 0x02, 0x05, 0x07, 0x19, 0xe0, 0x29, 0xe7, 0x15, 0x00, 0x25, 0x01, 0x75, 0x01, 0x95, 0x08, 0x81, 0x02, 0x95, 0x01, 0x75, 0x08, 0x81, 0x03, 0x95, 0x06, 0x75, 0x08, 0x15, 0x00, 0x25, 0x73, 0x05, 0x07, 0x19, 0x00, 0x29, 0x73, 0x81, 0x00, 0xc0,
    }};
    
    report makeReport(uint8_t modifiers = 0, uint8_t key1 = 0, uint8_t key2 = 0, uint8_t key3 = 0, uint8_t key4 = 0, uint8_t key5 = 0, uint8_t key6 = 0);
    
    report makeReport(uint8_t modifiers, uint8_t key1, uint8_t key2, uint8_t key3, uint8_t key4, uint8_t key5, uint8_t key6) {{
        return report {{ modifiers, 0x00, {{ key1, key2, key3, key4, key5, key6 }} }};
    }}
    
    void begin() {{
        static HIDSubDescriptor node(keyboardDescriptor, sizeof(keyboardDescriptor));
        HID().AppendDescriptor(&node);
    }}
    
    void send(report* k) {{
        HID().SendReport(2, (uint8_t*)k, sizeof(report));
    }}
    
    void release() {{
        prev_report = makeReport();
        send(&prev_report);
    }}

    void type(uint8_t key0, uint8_t key1, uint8_t key2, uint8_t key3, uint8_t key4, uint8_t key5, uint8_t modifiers) {{
        prev_report.keys[0] = key0;
        prev_report.keys[1] = key1;
        prev_report.keys[2] = key2;
        prev_report.keys[3] = key3;
        prev_report.keys[4] = key4;
        prev_report.keys[5] = key5;
        prev_report.modifiers = modifiers;
        send(&prev_report);
        release();
    }}
}}

void duckyString(const uint8_t* keys, size_t len) {{  
    for(size_t i = 0; i < len; i += 2) {{
        keyboard::type(pgm_read_byte_near(keys + i + 1), 0, 0, 0, 0, 0, pgm_read_byte_near(keys + i));
    }}
}}

{chr(10).join(string_blocks)}

void StartJob() {{
{chr(10).join(arduino_lines)}
}}

void setup() {{
    pinMode(buttonPin, INPUT_PULLUP);
    pinMode(greenLed, OUTPUT);
    keyboard::begin();
    delay(2000); // čakanie na inicializáciu HID
}}

void loop() {{
    if (digitalRead(buttonPin) == LOW) {{
        delay(50); // debouncing
        if (digitalRead(buttonPin) == LOW) {{
            StartJob();
            digitalWrite(greenLed, HIGH);
            delay(1000);
            digitalWrite(greenLed, LOW);
        }}
    }}
}}

// Created using local Duckify SK – full Slovak HID support
"""
    return full_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
