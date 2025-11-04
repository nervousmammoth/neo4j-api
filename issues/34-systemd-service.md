# Issue 34: Create Systemd Service Unit File

## Status
⏳ **TODO**

**Estimated Time:** 1 hour
**Branch:** `issue/34-systemd-service`
**Phase:** 8 - Deployment

## Description
Create `neo4j-api.service` systemd unit file for running the FastAPI application as a system service with automatic restart, logging, and proper resource management.

## Related Specifications
- [ ] **Reference:** `CLAUDE.md` - Production Deployment section

## Related BDD Tests
N/A - Configuration file

## Dependencies
- [ ] All application code complete

---

## Workflow Checklist

### 1️⃣ Create Service File
- [ ] Create `neo4j-api.service` unit file
- [ ] Configure service settings
- [ ] Configure environment
- [ ] Configure restart policy
- [ ] Configure logging

### 2️⃣ Documentation
- [ ] Add comments to service file
- [ ] Document installation steps
- [ ] Document service management commands

### 3️⃣ Validation
- [ ] Validate syntax
- [ ] Document deployment process

---

## Acceptance Criteria

### Functional Requirements
- [ ] Systemd unit file created
- [ ] Service runs as dedicated user
- [ ] Automatic restart configured
- [ ] Environment variables configured
- [ ] Working directory set
- [ ] Logging configured
- [ ] Dependencies declared

---

## Implementation Notes

### Example Service File

**`neo4j-api.service`:**
```ini
# Systemd service unit file for Neo4j API
# ========================================
# Installation:
#   sudo cp neo4j-api.service /etc/systemd/system/
#   sudo systemctl daemon-reload
#   sudo systemctl enable neo4j-api
#   sudo systemctl start neo4j-api
#
# Management:
#   sudo systemctl status neo4j-api
#   sudo systemctl restart neo4j-api
#   sudo systemctl stop neo4j-api
#   sudo journalctl -u neo4j-api -f

[Unit]
Description=Neo4j API - Linkurious-Compatible REST API
Documentation=https://github.com/your-org/neo4j-api
After=network.target neo4j.service
Wants=neo4j.service

[Service]
Type=notify
User=neo4j-api
Group=neo4j-api
WorkingDirectory=/opt/neo4j-api

# Environment
Environment="PATH=/opt/neo4j-api/venv/bin"
EnvironmentFile=/opt/neo4j-api/.env

# Execution
ExecStart=/opt/neo4j-api/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info

# Restart policy
Restart=always
RestartSec=5
StartLimitBurst=3
StartLimitInterval=60

# Resource limits
LimitNOFILE=65535
LimitNPROC=4096

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/neo4j-api/logs

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=neo4j-api

[Install]
WantedBy=multi-user.target
```

### Configuration Sections Explained

**[Unit] Section:**
- `Description` - Human-readable description
- `Documentation` - Link to documentation
- `After` - Start after network and Neo4j
- `Wants` - Soft dependency on Neo4j service

**[Service] Section:**
- `Type=notify` - Service notifies systemd when ready
- `User/Group` - Run as dedicated user (security)
- `WorkingDirectory` - Application directory
- `Environment` - PATH for venv
- `EnvironmentFile` - Load .env file
- `ExecStart` - Command to start service
- `Restart=always` - Always restart on failure
- `RestartSec` - Wait 5s before restart
- `StartLimitBurst/Interval` - Restart limits

**Security Hardening:**
- `NoNewPrivileges` - Prevent privilege escalation
- `PrivateTmp` - Private /tmp directory
- `ProtectSystem` - Read-only system directories
- `ProtectHome` - Protect user home directories
- `ReadWritePaths` - Allow writes only to logs

**Resource Limits:**
- `LimitNOFILE` - Max open files
- `LimitNPROC` - Max processes

**Logging:**
- `StandardOutput/Error=journal` - Log to systemd journal
- `SyslogIdentifier` - Identifier in logs

### Installation Steps

**1. Create dedicated user:**
```bash
sudo useradd --system --no-create-home --shell /bin/false neo4j-api
```

**2. Setup application directory:**
```bash
sudo mkdir -p /opt/neo4j-api
sudo chown neo4j-api:neo4j-api /opt/neo4j-api
```

**3. Deploy application:**
```bash
# Copy application files
sudo cp -r app/ /opt/neo4j-api/
sudo cp requirements.txt /opt/neo4j-api/
sudo cp .env /opt/neo4j-api/

# Create virtual environment
sudo -u neo4j-api python3 -m venv /opt/neo4j-api/venv
sudo -u neo4j-api /opt/neo4j-api/venv/bin/pip install -r /opt/neo4j-api/requirements.txt

# Set permissions
sudo chown -R neo4j-api:neo4j-api /opt/neo4j-api
sudo chmod 640 /opt/neo4j-api/.env
```

**4. Install service file:**
```bash
sudo cp neo4j-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable neo4j-api
sudo systemctl start neo4j-api
```

**5. Verify service:**
```bash
sudo systemctl status neo4j-api
sudo journalctl -u neo4j-api -f
curl http://localhost:8000/api/health
```

### Service Management Commands

**Start/Stop/Restart:**
```bash
sudo systemctl start neo4j-api
sudo systemctl stop neo4j-api
sudo systemctl restart neo4j-api
sudo systemctl reload neo4j-api  # Graceful reload
```

**Status and Logs:**
```bash
sudo systemctl status neo4j-api
sudo journalctl -u neo4j-api -f         # Follow logs
sudo journalctl -u neo4j-api -n 100     # Last 100 lines
sudo journalctl -u neo4j-api --since today
```

**Enable/Disable Autostart:**
```bash
sudo systemctl enable neo4j-api   # Start on boot
sudo systemctl disable neo4j-api  # Don't start on boot
```

### Alternative Configurations

**Development (manual start):**
```ini
[Service]
Type=simple
ExecStart=/opt/neo4j-api/venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Restart=no
```

**Production with Gunicorn:**
```ini
[Service]
ExecStart=/opt/neo4j-api/venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /opt/neo4j-api/logs/access.log \
    --error-logfile /opt/neo4j-api/logs/error.log
```

---

## Git Workflow

```bash
git checkout main && git pull origin main
git checkout -b issue/34-systemd-service

# Create service file
nano neo4j-api.service

# Add comprehensive configuration
# Add installation instructions

# Validate (syntax only, can't test without sudo)
cat neo4j-api.service

# Add to git
git add neo4j-api.service
git commit -m "feat(issue-34): create systemd service unit file"
git push origin issue/34-systemd-service
```

### Create Pull Request

```bash
gh pr create \
  --title "feat: create systemd service unit file" \
  --body "$(cat <<'EOF'
## Summary
- Created neo4j-api.service systemd unit file
- Automatic restart on failure
- Security hardening enabled
- Logging to systemd journal
- Documented installation and management

## Configuration Features
- Runs as dedicated user (neo4j-api)
- Automatic restart with backoff
- Resource limits configured
- Security hardening (NoNewPrivileges, ProtectSystem)
- Environment from .env file
- Depends on network and Neo4j service
- Logs to systemd journal

## Installation
See service file comments for installation steps.

## Testing
- [x] Service file syntax validated
- [x] Installation steps documented
- [x] Management commands documented

## Closes
Closes #34

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Verification Commands

```bash
# Validate syntax
systemd-analyze verify neo4j-api.service

# Check service file
cat /etc/systemd/system/neo4j-api.service

# After installation:
sudo systemctl status neo4j-api
sudo journalctl -u neo4j-api --no-pager
```

---

## References
- **Systemd Documentation:** https://www.freedesktop.org/software/systemd/man/systemd.service.html
- **Systemd Security:** https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Security

---

## Notes
- Service runs as dedicated user for security
- Automatic restart ensures high availability
- Security hardening options improve protection
- Logs go to systemd journal (use journalctl)
- Service starts after Neo4j service
- Resource limits prevent resource exhaustion
