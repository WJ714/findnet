# How FindNet works

FindNet is currently a single HTML file (`app/index.html`) that runs as a
[claude.ai Artifact](https://claude.ai). The Artifact runtime provides two things
the page cannot provide on its own: **sign-in** (`claude.use("user")`) and a
**shared database** (`claude.use("db")`). Everything else (UI, translations,
encryption, statistics) is plain browser JavaScript in the same file.

## Data model

| Path | Contents | Who can write |
|---|---|---|
| `activities/{id}` | title, place, day, time, minutes, MET value, side (`people` / `dogs`), dog-size rule, creator id | any signed-in contributor |
| `going/{uid}` | public joins and check-ins (only when the user's visibility is *Everyone*) | that user only |
| `shares/{uid}` | the same status, encrypted separately for each friend (visibility *Friends only*) | that user only |
| `follows/{uid}` | who this user follows; friends = mutual follows | that user only |
| `keys/{uid}` | public ECDH P-256 key | that user only |
| `outbox/{uid}/to/{friend}` | encrypted chat messages to one friend (last 100) | that user only |
| `profiles/{uid}` | nickname | that user only |
| `dogs/{uid}` | up to 3 dog profiles (name, breed, size, temperament, vaccinated) | that user only |
| `data/users/{uid}/settings` | visibility, block list, side, language | private to that user |
| `data/users/{uid}/mine` | joined activities, with a saved copy of each so history survives deletion | private to that user |
| `data/users/{uid}/profile` | body weight for calorie estimates | private to that user |
| `data/users/{uid}/keys` | private encryption key | private to that user |

The access rules that enforce the "who can write" column are in
`app/artifact-capabilities.json`. Publishing the page with those capabilities
recreates the same setup.

## Privacy and encryption

- Visibility has three settings: **Everyone**, **Friends only**, **Only me**.
- *Friends only* is enforced cryptographically, not by hiding UI: each user has an
  ECDH P-256 key pair; status and messages are encrypted with AES-GCM using a key
  derived for each pair of users. Anyone else, including blocked people, sees only
  ciphertext.
- Known limitations, to fix before a public launch:
  - The ECDH shared secret is used directly as the AES key (no HKDF step).
  - No forward secrecy; a leaked private key exposes past messages.
  - Metadata is visible: who has a conversation with whom, and when.
  - Private keys live in platform-private storage. Whoever controls the app's
    code and access rules could change that, so this protects users from each
    other, not from the operator.
- Location is never tracked. Activities are tied to a place and time, and the
  only presence signal is the optional "I'm here" check-in on the day.

## Moving off the Artifact runtime

To run FindNet as a standalone web app or WeChat Mini Program, replace:

1. `claude.use("user")` with your own sign-in (phone number, or `wx.login` plus a
   server-side `code2Session` exchange for WeChat).
2. `claude.use("db")` with your own backend that enforces the same per-user write
   rules listed above. The page only uses `doc().get/set/delete`,
   `collection().doc()`, and `onSnapshot` subscriptions, so the adapter is small.

Everything else can stay as it is.
