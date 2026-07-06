# Nexus Medic — Rock Pi Deployment

Voice-driven consultation assistant: records a conversation, transcribes it
locally with [Vosk](https://alphacephei.com/vosk/) (no audio sent to any
cloud STT service), generates a structured report via Gemini, saves it as a
`.docx`, and uploads it to the patient's record.

## 1. Flash & prep the OS

Any Debian/Armbian-based image for the Rock Pi 4C+ works. Then:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip \
    portaudio19-dev \
    espeak ffmpeg \
    libgpiod-dev gpiod
```

- `portaudio19-dev` — required to build PyAudio (mic input)
- `espeak` — required by `pyttsx3` for text-to-speech on Linux
- `gpiod` (CLI tools) — gives you `gpiodetect` / `gpioinfo` to find your button's chip/line

## 2. Copy this folder to the device

```bash
scp -r rockpi/ user@<rockpi-ip>:~/nexus-medic
```

(or `git clone`/`git pull` if you push this folder to a repo first)

## 3. Set up the virtual environment

```bash
cd ~/nexus-medic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Configure secrets

```bash
cp .env.example .env
nano .env
```

Fill in `GEMINI_API_KEY`, `AIRTABLE_TOKEN`, `AIRTABLE_BASE_ID`, and adjust
`AIRTABLE_TABLE_NAME` / `AIRTABLE_ID_FIELD` if your base differs.

## 5. Verify the physical button wiring

```bash
gpiodetect          # confirm your chip is /dev/gpiochip0 (adjust in main.py if not)
gpioinfo gpiochip0   # find the line offset your button is wired to
```

Update `BUTTON_GPIO_CHIP` / `BUTTON_LINE_OFFSET` at the top of `main.py` to match.
If no button is wired up (or setup fails for any reason), the app automatically
falls back to keyboard-only mode (press Enter to start/stop a session) — it
won't crash.

> Note: `main.py` uses the libgpiod v1.x Python API (`chip.get_line(...)`,
> `line.request(...)`). If the Rock Pi image ships libgpiod v2.x, that call
> will fail and the app will silently fall back to keyboard trigger only —
> check the printed message on startup to see which mode is active.

## 6. Speech recognition model

This folder already includes the Vosk small English model at
`models/vosk-model-small-en-us-0.15/` (~68MB), so no extra download is
needed — `main.py` picks it up automatically. To use a different model
(e.g. a larger one for better accuracy, or another language), download it
from https://alphacephei.com/vosk/models, place it anywhere on the device,
and set `VOSK_MODEL_PATH` in `.env` to point at it.

## 7. Edit the report prompt

`medical_prompt.txt` here is a starter template — review and adjust the
sections/wording to match your clinical reporting requirements before using
this in a real consultation.

## 8. Run it

```bash
source venv/bin/activate
python main.py
```

## 9. Optional: auto-start on boot (systemd)

```ini
# /etc/systemd/system/nexus-medic.service
[Unit]
Description=Nexus Medic consultation assistant
After=network-online.target sound.target
Wants=network-online.target

[Service]
WorkingDirectory=/home/rock/nexus-medic
ExecStart=/home/rock/nexus-medic/venv/bin/python main.py
Restart=on-failure
User=rock

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nexus-medic
journalctl -u nexus-medic -f   # watch logs
```
