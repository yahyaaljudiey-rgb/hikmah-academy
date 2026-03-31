# Deferred Features

## Zoom Integration

Deferred until Zoom account admin / marketplace access is available.

- Academy official timezone for Zoom tracking: `Europe/London`.
- Arabic class monitoring window:
  - official start: `09:00` London time
  - official end: `09:50` London time
  - allowed early join: `08:55` London time
- Teacher location does not change compliance rules; all checks are based on London time, including winter/summer time changes.
- Connect Zoom to the system using Server-to-Server OAuth and webhooks.
- Match each Zoom meeting to its class using the class Zoom link / meeting identity.
- Limit automatic ingestion to the Arabic teaching period only.
- Automatically import cloud recordings into the correct class without mixing classes.
- Store for each imported lesson:
  - day
  - date
  - lesson title
  - recording link
  - short lesson summary
- Show missing or delayed recordings in the supervisor dashboard.
- Track teacher entry time, exit time, and session duration from Zoom meeting data.
- Compare Zoom session timing with the scheduled class time to detect late start or early exit.
- Pull previous cloud recordings related to each class when Zoom access becomes available.
