# Security

This is a living checklist. Update it when the system changes.

## Threat model (quick)
- What are you protecting? (user data, tokens, billing, reputation)
- Likely adversaries: opportunistic bots, credential stuffers, targeted attackers
- Common attack surfaces: exposed ports, webhook endpoints, auth flows, file uploads

## Secure defaults
- Only 80/443 public. App ports bind to 127.0.0.1.
- Least privilege runtime users (avoid running app processes as root).
- Secrets never in repo; use env vars or a secrets manager.
- Add rate limiting at the edge (Cloudflare/WAF) and at Nginx.
- Strict CORS policy for APIs.
- Disable debug endpoints in production.

## Monthly checks (suggested)
### Network & exposure
- Confirm Node/app ports are not publicly reachable.
- Confirm firewall rules match intended exposure.
- Confirm Cloudflare/WAF/rate limiting is enabled.

### Patch hygiene
- OS security updates
- Dependency updates (Node/Python/etc.)
- Scan for vulnerable packages

### Logs & anomalies
- Review top IPs, routes, status codes
- Look for spikes, repeated 404/401, suspicious paths (/.env, /.git, wp-login)

## Incident basics
- Contain: block exposed ports, disable compromised keys, rotate secrets
- Eradicate: remove malicious artifacts, patch vulnerabilities
- Recover: redeploy clean build, verify integrity
- Learn: update docs, add detection/prevention

## Commands (Linux server quick checks)
```bash
# what is listening
sudo ss -tulpn

# firewall status
sudo ufw status verbose

# nginx syntax and status
sudo nginx -t && sudo systemctl status nginx --no-pager

# app status (pm2)
sudo pm2 status
sudo pm2 logs --lines 200
```
