# Clinician Monitor Service

## How it works

Every 30 seconds, the service checks the location of each clinician against their safe zone. If a clinician is outside their zone, an email alert is sent immediately. Every 2 minutes after that, a follow-up alert is sent with how long they've been out. When they re-enter their zone, a final alert is sent confirming they're back.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in:
```bash
cp .env.example .env
```

3. Run:
```bash
python main.py
```

## Testing
```bash
python test_main.py
```

## Notes

- Errors send email alerts and also log to `errors.txt`
- Emails are sent in a background thread so they don't block the polling loop
