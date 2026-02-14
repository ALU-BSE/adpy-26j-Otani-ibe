IshemaLink Threat Model
This document identifies three major security risks to the IshemaLink platform and explains how my code protects the system from these threats.

1. Risk: Brute-Force Password Guessing
Threat: A hacker or an automated "bot" tries to guess an agent's password by submitting thousands of login attempts.

Impact: If successful, the attacker gains full access to the agent's account and private logistics data.

Mitigation ( Fix): I implemented Rate Limiting using Django REST Framework's AnonRateThrottle. The code limits users to 5 login attempts per minute. If they exceed this, the system automatically blocks their IP address, making it impossible to guess passwords quickly.

2. Risk: Data Theft from Database Breach
Threat: A hacker manages to break into the main server and steals the entire user database.

Impact: Without protection, the hacker would see every user's 16-digit Rwandan National ID (NID) in plain text, leading to massive identity theft.

Mitigation: I implemented Field-Level Encryption (AES-128) using the cryptography library. Before a NID is ever saved to the database, our encrypt_nid function scrambles it into a random string of characters. Even if a hacker steals the database, the IDs are unreadable without my secret key.

3. Risk: Insider Threat (Rogue Agent)
Threat: A person who is legally allowed to use the system (like a real agent) starts looking at private customer IDs for their own personal gain.

Impact: The customer's privacy is violated by an internal employee who has no business reason to see that data.

Mitigation (Fix): I implemented two layers of protection. First, we use Data Masking to show only parts of the ID (e.g., 1199**********00), preventing casual viewing. Second, we created a Security Audit Log. Every time anyone views a profile, our code automatically saves their username and the exact time in a permanent record. This makes it easy to catch and punish "rogue" behavior.