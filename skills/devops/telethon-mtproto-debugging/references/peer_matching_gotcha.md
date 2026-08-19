# Peer-matching gotcha — reproduction & verification recipe

## Symptom (tgf / tg-cli class forwarders)
- `--rebuild-cache` / `--force-rebuild` wipes the real dedup cache, then the run
  re-forwards the ENTIRE source (duplicate storm).
- Final "VERIFIED" count prints `0` / `n/a`.
- `dedupe` reports "No duplicates to remove" even though copies clearly exist.
- Works fine when SOURCE is a *user*, breaks when SOURCE is a *channel*.

## Root cause
Telegram stores a forwarded message's `Message.fwd_from.saved_from_peer` typed by
the original sender. For a channel source the stored type is `PeerChannel`, but the
code compared it to a hardcoded `PeerUser(src.id)`, which is never equal.

Confirmed offline (no network, no session) with:

```python
from datetime import datetime
from telethon.tl.types import PeerUser, PeerChannel, MessageFwdHeader
from telethon import utils

src_id_channel = -1001961116802   # repo's SOURCE_CHANNELS (a channel)
src_id_user = 558372819

fwd_channel = MessageFwdHeader(date=datetime.now(),
                              saved_from_peer=PeerChannel(1961116802),
                              saved_from_msg_id=42)
fwd_user = MessageFwdHeader(date=datetime.now(),
                            saved_from_peer=PeerUser(558372819),
                            saved_from_msg_id=42)

# BUGGY check — always False for channel source
print(fwd_channel.saved_from_peer == PeerUser(src_id_channel))   # -> False

# FIXED check
print(fwd_channel.saved_from_peer == utils.get_peer(src_id_channel))  # -> True
print(fwd_user.saved_from_peer == utils.get_peer(src_id_user))        # -> True
```

Note `MessageFwdHeader.__init__` requires a `date` kwarg (TypeError without it).

## Fix
Replace every `getattr(fwd, "saved_from_peer", None) == PeerUser(src.id)` with a
helper using `utils.get_peer(src_id)` so the comparison uses the correct peer
type. Route all four sites through it (recency scan, full scan, final
verification, dedupe).

## Regression test (offline)
```python
def test_is_from_source_matches_channel_and_user():
    from tgforwarder.cli import _is_from_source
    from telethon.tl.types import PeerChannel, PeerUser, MessageFwdHeader
    from datetime import datetime
    fwd_chan = MessageFwdHeader(date=datetime.now(),
                               saved_from_peer=PeerChannel(1961116802), saved_from_msg_id=1)
    fwd_user = MessageFwdHeader(date=datetime.now(),
                               saved_from_peer=PeerUser(558372819), saved_from_msg_id=1)
    assert _is_from_source(fwd_chan, -1001961116802) is True
    assert _is_from_source(fwd_user, 558372819) is True
    assert _is_from_source(fwd_chan, 558372819) is False
    assert _is_from_source(None, -1001961116802) is False
```
This was the test added to `tests/test_offline.py` in the tgforwarder repo
(/home/deeone/Documents/scraper/python-scraper/tgforwarder) — 18 passed after fix.

## Why it went unnoticed
The repo's OTHER configured source is a user (558372819), so PeerUser==PeerUser
passed and the channel path was never exercised by manual runs or tests.
