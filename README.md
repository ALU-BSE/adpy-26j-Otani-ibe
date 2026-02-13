IshemaLink: Secure Logistics Platform
IshemaLink is a logistics application built with Django 6.0.1, designed with a focus on data security and privacy for users in Rwanda. This project implements a high-security hardening layer to protect Personally Identifiable Information (PII) and prevent unauthorized access.

Security Decisions
1. Rate Limiting Strategy
Decision: Implemented a LoginAttemptThrottle with a limit of 5 attempts per minute.

Why: I chose this limit to balance user experience with security. A human agent may occasionally forget a password, but more than five attempts in a minute typically signals a Brute-Force or Credential Stuffing attack. By throttling at the application level, I preserve server resources and protect user accounts.

2. Token Expiry & Management
Decision: Access tokens expire in 15 minutes, while Refresh tokens expire in 24 hours.

Why: Short-lived access tokens ensure that if a token is intercepted, its utility is highly restricted. The 24-hour refresh window is designed to match a standard logistics shift, allowing agents to stay "LockedIn" to their work without repeated logins, provided their session remains active.

3. Encryption Standard
Decision: Utilized Fernet (AES-128) symmetric encryption for Rwandan National IDs.

Why: Unlike simple hashing, you need to occasionally view the ID for verification. Fernet ensures the data is "scrambled" at rest in the database, satisfying compliance requirements for sensitive PII.