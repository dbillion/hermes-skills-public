# Disk and Memory Cleanup Tips for MCP Server Workloads

When running MCP servers (especially Burp Suite, OpenCTI, etc.) on systems with limited resources, regular maintenance can prevent performance issues.

## Disk Space Management

### Common Space Consumers
- Browser caches (Chrome, Brave, Firefox, etc.)
- Language/tool caches (pip, npm, uv, etc.)
- Container/runtime caches (Docker, Podman, Java, etc.)
- Snap package revisions
- Journal logs
- Application-specific caches (e.g., Puppeteer, codex-runtimes)

### Safe Cleanup Commands
```bash
# Browser caches (adjust paths as needed)
rm -rf ~/.cache/browseruse/*
rm -rf ~/.cache/google-chrome/Cache/* ~/.cache/google-chrome/Code\ Cache/* ~/.cache/google-chrome/GPUCache/*
rm -rf ~/.cache/BraveSoftware/*
rm -rf ~/.cache/mozilla/*

# Language caches
rm -rf ~/.cache/pip/*
rm -rf ~/.npm/_cacache/*   # if using npm
rm -rf ~/.cache/uv/        # if using uv

# Snap revisions (removes disabled versions)
sudo snap list --all | awk '/disabled/{print $1, $3}' |
  while read snapname revision; do
    sudo snap remove "$snapname" --revision="$revision"
  done

# Journal logs (keep last 3 days)
sudo journalctl --vacuum-time=3d

# Pacman cache (remove uninstalled packages)
sudo pacman -Sc

# Orphaned packages
sudo pacman -Rns $(pacman -Qtdq)
```

### Finding Large Files/Directories
```bash
# Check home directory usage
du -sh ~/* 2>/dev/null | sort -hr | head -20

# Check specific caches
du -sh ~/.cache/* 2>/dev/null | sort -hr | head -10

# Find large files in Downloads
find ~/Downloads -type f -size +100M -exec du -h {} + | sort -hr
```

## Memory & Swap Management

### Monitoring
```bash
# Memory usage
free -h

# Top memory consumers
top -o %MEM

# Swap usage
swapon --show
```

### Reducing Pressure
- Close unused browser tabs/applications (especially Chrome/Brave/Firefox)
- Stop unused containers/VMs
- Restart memory-heavy services (e.g., Java-based Burp Suite if leaking)
- Consider temporarily increasing swap if needed (but prefer reducing usage)

### Java-Specific Notes (for Burp Suite)
- Use Java 21+: `sudo pacman -S jdk21-openjdk && sudo archlinux-java set java-21-openjdk`
- Monitor Java heap usage if running large scans
- Restart Burp Suite periodically if memory grows unbounded

## MCP Server Specific Tips

### Burp Suite
- Ensure proper extension installation (not as Java agent)
- Monitor Burp Suite memory usage during long scans
- Consider limiting scan scope or using incremental scans

### OpenCTI
- Ensure PostgreSQL is properly configured and vacuumed
- Monitor connector logs for memory leaks

### General
- Use `hermes mcp test <name>` periodically to verify responsiveness
- Check MCP server logs for errors or restart loops
- Consider setting up lightweight health checks for critical servers

## When to Clean
- Before starting large MCP-assisted tasks
- When disk usage exceeds 80%
- When swap usage is consistently high (>50%)
- After completing major operations (scans, imports, etc.)