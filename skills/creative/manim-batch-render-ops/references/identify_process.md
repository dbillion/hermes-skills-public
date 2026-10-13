# Identify a mystery high-RAM process before killing it

Use when renders are slow / load average is high and you suspect another process is competing
for CPU or RAM. Always confirm with the user before stopping a system-level service.

## 1. Find the heavy process
```bash
ps -eo pid,ppid,etime,rss,args | grep -iE "java|python|node" | grep -v grep
# rss is in KB. /1024 ≈ MB, /1024/1024 ≈ GB.
# etime = how long it has been running.
```
Example: PID 14713, `rss=3057192` (~2.9 GB), `etime=3-09:20:43` (3 days),
args `/usr/share/elasticsearch/jdk/bin/java ...` -> Elasticsearch.

## 2. Is it serving anything? (idle check)
```bash
ss -ltnp 2>/dev/null | grep -E "9200|9300" || echo "port closed -> idle"
```
Closed port + idle 3 days => safe to stop (not actively used).

## 3. Is it a tracked system service or manually launched?
```bash
systemctl list-units --all 2>/dev/null | grep -i elasticsearch   # tracked unit?
pacman -Qo /usr/share/elasticsearch/jdk/bin/java 2>/dev/null || echo "not a package"
ps -p <ppid> -o pid,args   # parent chain
```
- If `systemctl stop <unit>` works -> clean stop (may restart on boot unless `disable`).
- If "unit not loaded" but process alive -> launched manually. Stop via PID:
  ```bash
  kill -TERM <pid>            # graceful
  sleep 3
  ps -p <pid> >/dev/null && kill -KILL <pid>   # force if still alive
  ```

## 4. Confirm removal
```bash
ps -eo comm | grep -i java || echo "no java procs"
for d in /usr/share/elasticsearch /var/lib/elasticsearch /etc/elasticsearch /opt/elasticsearch; do
  [ -e "$d" ] && echo "EXISTS $d" || echo "gone $d"
done
ss -ltn | grep -E "9200|9300" || echo "ports closed"
```

## Real example this session
Idle Elasticsearch (PID 14713, 2.9 GB, port 9200 closed, unrelated to the DSA gradle
project). User chose clean stop; `systemctl stop elasticsearch` reported "unit not loaded"
(manual launch), so PIDs were SIGTERM'd then SIGKILL'd. Result: 0 java procs, ~2.9 GB RAM
freed, load average dropped, both manim render batches ran faster. No data loss.
