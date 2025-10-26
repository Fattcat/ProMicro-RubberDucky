#include <SPI.h>
#include <SD.h>
#include <HID.h>

// === PINY ===
const int buttonPin = 2;   // tlačidlo na D2
const int greenLed = 13;   // LED
const int chipSelect = 10; // SD karta CS

// === HID RAW ===
namespace keyboard {
    typedef struct report {
        uint8_t modifiers;
        uint8_t reserved;
        uint8_t keys[6];
    } report;

    report prev_report = report { 0x00, 0x00, { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 } };

    const uint8_t keyboardDescriptor[] PROGMEM = {
        0x05, 0x01, 0x09, 0x06, 0xa1, 0x01, 0x85, 0x02, 0x05, 0x07, 0x19, 0xe0, 0x29, 0xe7, 0x15, 0x00,
        0x25, 0x01, 0x75, 0x01, 0x95, 0x08, 0x81, 0x02, 0x95, 0x01, 0x75, 0x08, 0x81, 0x03, 0x95, 0x06,
        0x75, 0x08, 0x15, 0x00, 0x25, 0x73, 0x05, 0x07, 0x19, 0x00, 0x29, 0x73, 0x81, 0x00, 0xc0,
    };

    void begin() {
        static HIDSubDescriptor node(keyboardDescriptor, sizeof(keyboardDescriptor));
        HID().AppendDescriptor(&node);
    }

    void send(report* k) {
        HID().SendReport(2, (uint8_t*)k, sizeof(report));
    }

    void release() {
        prev_report = report { 0x00, 0x00, { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 } };
        send(&prev_report);
    }

    void type(uint8_t key0, uint8_t key1 = 0, uint8_t key2 = 0, uint8_t key3 = 0, uint8_t key4 = 0, uint8_t key5 = 0, uint8_t modifiers = 0) {
        prev_report.keys[0] = key0;
        prev_report.keys[1] = key1;
        prev_report.keys[2] = key2;
        prev_report.keys[3] = key3;
        prev_report.keys[4] = key4;
        prev_report.keys[5] = key5;
        prev_report.modifiers = modifiers;
        send(&prev_report);
        release();
    }
}

// === SK QWERTY KEYMAP (modifier, keycode) ===
struct KeyMap {
    char c;
    uint8_t mod;
    uint8_t key;
};

// Zjednodušená verzia – len najčastejšie znaky
const KeyMap sk_map[] PROGMEM = {
    // Základ
    {'a', 0, 4}, {'b', 0, 5}, {'c', 0, 6}, {'d', 0, 7}, {'e', 0, 8}, {'f', 0, 9},
    {'g', 0, 10}, {'h', 0, 11}, {'i', 0, 12}, {'j', 0, 13}, {'k', 0, 14}, {'l', 0, 15},
    {'m', 0, 16}, {'n', 0, 17}, {'o', 0, 18}, {'p', 0, 19}, {'q', 0, 20}, {'r', 0, 21},
    {'s', 0, 22}, {'t', 0, 23}, {'u', 0, 24}, {'v', 0, 25}, {'w', 0, 26}, {'x', 0, 27},
    {'y', 0, 28}, {'z', 0, 29},

    {'A', 2, 4}, {'B', 2, 5}, {'C', 2, 6}, {'D', 2, 7}, {'E', 2, 8}, {'F', 2, 9},
    {'G', 2, 10}, {'H', 2, 11}, {'I', 2, 12}, {'J', 2, 13}, {'K', 2, 14}, {'L', 2, 15},
    {'M', 2, 16}, {'N', 2, 17}, {'O', 2, 18}, {'P', 2, 19}, {'Q', 2, 20}, {'R', 2, 21},
    {'S', 2, 22}, {'T', 2, 23}, {'U', 2, 24}, {'V', 2, 25}, {'W', 2, 26}, {'X', 2, 27},
    {'Y', 2, 28}, {'Z', 2, 29},

    {'1', 0, 30}, {'2', 0, 31}, {'3', 0, 32}, {'4', 0, 33}, {'5', 0, 34},
    {'6', 0, 35}, {'7', 0, 36}, {'8', 0, 37}, {'9', 0, 38}, {'0', 0, 39},

    {' ', 0, 44}, {'\n', 0, 40}, {'\t', 0, 43},

    // Špeciálne znaky (SK QWERTY)
    {'!', 2, 30}, {'"', 2, 34}, {'#', 64, 11}, {'$', 2, 35}, {'%', 2, 36},
    {'&', 2, 37}, {'\'', 0, 52}, {'(', 2, 38}, {')', 2, 39}, {'*', 2, 55},
    {'+', 64, 27}, {',', 0, 54}, {'-', 0, 45}, {'.', 0, 55}, {'/', 0, 56},
    {':', 2, 54}, {';', 0, 51}, {'<', 64, 28}, {'=', 0, 46}, {'>', 64, 29},
    {'?', 2, 56}, {'@', 64, 20}, {'[', 64, 9}, {'\\', 64, 26}, {']', 64, 10},
    {'^', 64, 35}, {'_', 2, 45}, {'`', 0, 53}, {'{', 64, 21}, {'|', 64, 49},
    {'}', 64, 22}, {'~', 64, 53},

    // Diakritika
    {'á', 64, 52}, {'Á', 66, 52},
    {'ä', 64, 9},  {'Ä', 66, 9},
    {'č', 64, 6},  {'Č', 66, 6},
    {'ď', 64, 7},  {'Ď', 66, 7},
    {'é', 64, 8},  {'É', 66, 8},
    {'í', 64, 12}, {'Í', 66, 12},
    {'ĺ', 64, 51}, {'Ĺ', 66, 51},
    {'ľ', 64, 15}, {'Ľ', 66, 15},
    {'ň', 64, 17}, {'Ň', 66, 17},
    {'ó', 64, 18}, {'Ó', 66, 18},
    {'ô', 66, 18}, {'Ô', 66, 18},
    {'ŕ', 64, 21}, {'Ŕ', 66, 21},
    {'š', 64, 22}, {'Š', 66, 22},
    {'ť', 64, 23}, {'Ť', 66, 23},
    {'ú', 64, 24}, {'Ú', 66, 24},
    {'ý', 64, 28}, {'Ý', 66, 28},
    {'ž', 64, 29}, {'Ž', 66, 29},
    {'€', 64, 8},
};

const int map_size = sizeof(sk_map) / sizeof(sk_map[0]);

void sendChar(char c) {
    for (int i = 0; i < map_size; i++) {
        KeyMap km;
        memcpy_P(&km, &sk_map[i], sizeof(km));
        if (km.c == c) {
            keyboard::type(km.key, 0, 0, 0, 0, 0, km.mod);
            return;
        }
    }
    // Ak znak nie je v mape, ignoruj (alebo loguj cez Serial)
}

void sendString(const String& str) {
    for (int i = 0; i < str.length(); i++) {
        sendChar(str[i]);
    }
}

void executeCommand(String line) {
    line.trim();
    if (line.length() == 0 || line.startsWith("REM")) return;

    int firstSpace = line.indexOf(' ');
    String cmd = (firstSpace == -1) ? line : line.substring(0, firstSpace);
    String arg = (firstSpace == -1) ? "" : line.substring(firstSpace + 1);

    cmd.toUpperCase();

    if (cmd == "DELAY") {
        delay(arg.toInt());
    }
    else if (cmd == "STRING") {
        sendString(arg);
    }
    else if (cmd == "ENTER") {
        keyboard::type(40);
    }
    else if (cmd == "TAB") {
        keyboard::type(43);
    }
    else if (cmd == "SPACE") {
        keyboard::type(44);
    }
    else if (cmd == "GUI" || cmd == "WINDOWS") {
        if (arg == "r" || arg == "R") {
            keyboard::type(21, 0, 0, 0, 0, 0, 8);
        } else if (arg == "m" || arg == "M") {
            keyboard::type(16, 0, 0, 0, 0, 0, 8);
        } else if (arg.length() == 1 && isAlpha(arg[0])) {
            uint8_t kc = tolower(arg[0]) - 'a' + 4;
            keyboard::type(kc, 0, 0, 0, 0, 0, 8);
        }
    }
    else if (cmd == "ALT" && arg == "TAB") {
        keyboard::type(43, 0, 0, 0, 0, 0, 4);
    }
    else if (cmd == "UP") {
        keyboard::type(82);
    }
    else if (cmd == "DOWN") {
        keyboard::type(81);
    }
    else if (cmd == "LEFT") {
        keyboard::type(80);
    }
    else if (cmd == "RIGHT") {
        keyboard::type(79);
    }
    // Možno rozšíriť o ďalšie príkazy
}

void runPayload() {
    if (!SD.begin(chipSelect)) {
        // Ak SD karta nefunguje, LED blikne 3x
        for (int i = 0; i < 3; i++) {
            digitalWrite(greenLed, HIGH);
            delay(250);
            digitalWrite(greenLed, LOW);
            delay(250);
        }
        return;
    }

    File file = SD.open("inject.txt");
    if (!file) {
        // Súbor neexistuje – blikni 2x
        for (int i = 0; i < 2; i++) {
            digitalWrite(greenLed, HIGH);
            delay(300);
            digitalWrite(greenLed, LOW);
            delay(300);
        }
        return;
    }

    while (file.available()) {
        String line = file.readStringUntil('\n');
        executeCommand(line);
    }
    file.close();

    // Úspech – rozsvietiť na 1s
    digitalWrite(greenLed, HIGH);
    delay(1000);
    digitalWrite(greenLed, LOW);
}

void setup() {
    pinMode(buttonPin, INPUT_PULLUP);
    pinMode(greenLed, OUTPUT);
    digitalWrite(greenLed, LOW);

    keyboard::begin();
    delay(2000); // čakaj na pripojenie ako HID
}

void loop() {
    if (digitalRead(buttonPin) == LOW) {
        delay(50); // debouncing
        if (digitalRead(buttonPin) == LOW) {
            runPayload();
        }
    }
}
