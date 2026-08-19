# Social Platform Tool Inventory (Agent Reach + OpenCLI + linkedin-scraper-mcp)

Captured from a live session. Commands are `opencli <platform> <command> [--format yaml|json]`.
All adapters share common options: `-f/--format` (table/plain/json/yaml/md/csv),
`--window foreground|background`, `--site-session ephemeral|persistent`, `--keep-tab bool`.

## LinkedIn — two backends
### linkedin-scraper-mcp (MCP tools, the Agent Reach backend)
Read + connect + message ONLY. No apply / upload-CV / fill-form.
- get_my_profile() / get_person_profile(username, sections?, max_scrolls?)
- search_people(keywords, location?, network?, current_company?)
- get_company_profile / get_company_employees / get_company_posts / search_companies
- search_jobs(keywords, location?, max_pages?, date_posted?, job_type?, experience_level?, work_type?, easy_apply?, sort_by?)
- get_job_details(job_url) / get_saved_jobs(max_pages?)
- get_feed / search_posts / get_sidebar_profiles
- connect_with_person / send_message / get_inbox / get_conversation / search_conversations
- close_session

### opencli linkedin (browser bridge, richer write surface)
- read: whoami, profile-read, profile-experience, profile-projects, profile-analytics, posts, post-analytics, timeline, search, people-search, job-detail, jobs-preferences, inbox, thread-snapshot, sent-invitations, services-read, salesnav-* (Sales Navigator)
- write (fail-closed): connect <profile-url> (verifies profile before sending note), safe-send (verifies thread/recipient before sending), salesnav-message

## Twitter / X — opencli twitter
- read: whoami, profile, timeline (--type following for chronological), search, thread, article, bookmarks, bookmark-folders, bookmark-folder, likes, followers, following, lists, list-tweets, notifications, device-follow, download
- write: post, reply, quote, retweet, like, follow, follow-batch, block, unblock, mute-ish (hide-reply), bookmark, unbookmark, unlike, unfollow, unretweet, list-create/delete/add/remove (+ -batch), delete, reply-dm, accept (auto-accept DMs by keyword)

## Reddit — opencli reddit
- read: whoami, home (personalized), frontpage, popular, hot, read <post-id>, search, subreddit <name>, subreddit-info, subscribed, saved, upvoted, user, user-posts, user-comments
- write: comment <post-id> <text>, reply <comment-id> <text>, save/unsave, upvote (up/down), subscribe/unsubscribe

## Instagram — opencli instagram
- read: whoami, profile, user, explore, search, followers, following, saved (optionally by collection), download, story (read)
- write: post (feed/carousel), reel, story, note, comment, like, unlike, follow, unfollow, save, unsave, collection-create/delete

## Facebook — opencli facebook
- read: whoami, profile, feed, friends, groups, events, memories, notifications, marketplace-listings, marketplace-inbox, search
- write: add-friend, join-group

## OpenCLI browser bridge — opencli browser <profile> <cmd>
profile alias e.g. `hg5rwhdy` (get via `opencli profile list`). Commands:
analyze, back, bind, check, click, close, console, dblclick, dialog, drag, eval,
extract, fill, find, focus, frames, get, hover, init, keys, network, open, screenshot,
scroll, select, state, tab, type, unbind, uncheck, upload, verify, wait.
Use `eval` for JS in page context (cannot read HttpOnly cookies — only document.cookie).
Use `network` for response-shape capture (does NOT capture outgoing request headers/Cookie).

## Agent Reach CLI — agent-reach <cmd>
setup, install, configure (--from-browser chrome FAILS on keychain), doctor,
uninstall, skill, format, transcribe (Whisper via Groq/OpenAI), check-update, watch, version.
`doctor` shows connected platforms (13/15 base; 5 social via OpenCLI + 1 via linkedin-scraper-mcp).
