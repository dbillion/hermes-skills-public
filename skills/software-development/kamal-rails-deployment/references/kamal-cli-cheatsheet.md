# Kamal CLI Cheatsheet

## Setup
```bash
kamal init                    # Create config/deploy.yml, .kamal/secrets, hooks
kamal setup                   # Build image, push, deploy (first time)
```

## Deploy
```bash
kamal deploy                  # Full deploy (build + push + launch)
kamal deploy --skip-build     # Skip image build (code-only deploy)
kamal redeploy                # Deploy without rebuilding image
```

## Inspection
```bash
kamal logs -f                 # Tail all logs
kamal logs -r job             # Tail job logs only
kamal info                    # Show containers, images, status
kamal containers              # List running containers
```

## Access
```bash
kamal console                 # Rails console on server
kamal shell                   # Bash on server
kamal dbc                     # Database console (psql)
```

## Accessories
```bash
kamal accessory boot db      # Start DB accessory only
kamal accessory boot redis    # Start Redis accessory only
kamal accessory upload db config/postgres/production.conf  # Upload config file
```

## Maintenance
```bash
kamal rollback                # Rollback to previous version
kamal prune all               # Remove old images/containers
kamal clean                   # Remove unused images
```

## Hooks (in .kamal/hooks/)
```bash
# pre-deploy — runs before deploy
# post-deploy — runs after deploy
# pre-build — runs before image build
# post-build — runs after image build
```

## Common Issues
- **Port already allocated**: Another service is using 5432/6379. Change local docker-compose ports.
- **Image push fails**: Check `KAMAL_REGISTRY_PASSWORD` in `.kamal/secrets`
- **DB connection refused**: Verify `DB_HOST` matches accessory name, not localhost
- **Assets 404**: Ensure `config.assets.compile = false` in production.rb and assets are precompiled
