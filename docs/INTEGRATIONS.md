# Integration Setup

All real credentials belong in your local `.env` file. Never commit them to GitHub.

## Groq AI

1. Create a Groq API key.
2. Copy `.env.example` to `.env`.
3. Set `GROQ_API_KEY=...`.

## Gmail or SMTP/IMAP email

Use an app password, not your normal account password.

```env
JARVIS_EMAIL_ADDRESS=you@gmail.com
JARVIS_EMAIL_APP_PASSWORD=your_app_password
JARVIS_SMTP_HOST=smtp.gmail.com
JARVIS_SMTP_PORT=587
JARVIS_IMAP_HOST=imap.gmail.com
```

## Twilio WhatsApp / phone

```env
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_WHATSAPP=whatsapp:+14155238886
TWILIO_FROM_PHONE=+15551234567
```

## Spotify

Create a Spotify developer app and set:

```env
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

## Home Assistant

```env
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=your_long_lived_access_token
```

## Wake-on-LAN

Enable Wake-on-LAN in BIOS/UEFI and network adapter settings, then set:

```env
JARVIS_TARGET_PC_MAC=AA:BB:CC:DD:EE:FF
JARVIS_TARGET_PC_BROADCAST=255.255.255.255
```
