# Security Policy

## Supported Versions

Moonlygram is pre-1.0; security fixes are released against the latest version only.

| Version    | Supported |
| ---------- | --------- |
| latest 0.x | ✅        |
| older      | ❌        |

## Reporting a Vulnerability

Please **do not open a public issue** for security vulnerabilities.

Report privately through GitHub's [private vulnerability reporting](https://github.com/AtarixiaFamine/Moonlygram/security/advisories/new)
(the repo's **Security → Report a vulnerability** button). Include:

- a description of the issue and its impact,
- steps to reproduce (a minimal proof of concept if possible),
- the affected version(s).

Expect an acknowledgement within a few days. Once confirmed, I'll prepare and
release a fix and credit you in the advisory unless you'd rather stay anonymous.
Please allow a reasonable window before any public disclosure.

## Scope

Moonlygram is an HTTP client for the Telegram Bot API. Your **bot token is a
secret**: keep it out of source control and logs, and set the `secret_token`
option on webhooks so you can verify requests really come from Telegram. Token
leakage in your own code is outside this project's scope.
