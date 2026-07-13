# Security Policy

## Reporting a vulnerability

Email [almond.ony@gmail.com](mailto:almond.ony@gmail.com) with details. Please do not open a public issue for security-sensitive reports.

## Secrets and credentials

- Never commit M-Pesa Daraja credentials, API keys, or production secrets.
- Copy from the env example file into a local `.env` (or equivalent) and keep that file out of git.
- Rotate any key that may have been exposed.
