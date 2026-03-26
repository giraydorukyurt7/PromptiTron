# PromptiTron Deployment with Dokploy

This guide explains how to deploy PromptiTron on Dokploy using Docker Compose.

## Prerequisites

Before deploying, make sure you have:

- a Dokploy account
- a Git repository containing the project
- a valid Google API key
- a working `docker-compose.yml`
- optional custom domain configuration if you do not want to use the default Dokploy subdomain

## Create a New Dokploy Application

1. Log in to Dokploy
2. Click **New Application**
3. Choose **Docker Compose**
4. Set a project name such as:

```text
promptitron
```

## Connect the Repository

In the repository configuration:

- **Repository URL**: your Git repository URL
- **Branch**: `main`
- **Docker Compose File**: `docker-compose.yml`

Example:

```text
Repository URL: https://github.com/your-username/PromptiTron.git
Branch: main
Docker Compose File: docker-compose.yml
```

## Environment Variables

Set the required environment variables in Dokploy:

```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash
TEMPERATURE=0.7
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
CHROMA_HOST=chroma-db
CHROMA_PORT=8000
MONITOR_PORT=8002
```

Optional variables can be added depending on your production setup.

## Deploy

After configuring the repository and environment variables:

1. Click **Deploy**
2. Wait for the build to complete
3. Review build logs and runtime logs
4. Verify that the containers are healthy

## Typical Service Layout

A Dokploy deployment may include:

- **API service**
- **ChromaDB service**
- **worker service**
- **monitoring service**
- **frontend service** (if included in the compose setup)

## Post-Deployment Checks

### API health

```bash
curl https://your-app.dokploy.app/health
```

### API docs

```text
https://your-app.dokploy.app/docs
```

### Monitor health

```bash
curl https://your-app-monitor.dokploy.app/health
```

## Domain Configuration

### Default Dokploy subdomain
Dokploy can generate a default application URL automatically.

### Custom domain
If you use a custom domain:

1. Add the domain in Dokploy
2. Configure DNS according to Dokploy instructions
3. Wait for DNS propagation
4. Verify SSL provisioning

## Redeploy Workflow

### Manual redeploy
Use the **Redeploy** button in Dokploy after pushing changes.

### Automatic redeploy
Enable repository webhook or auto-deploy if you want deployments to trigger after each push to the selected branch.

## Troubleshooting

### Build failure
- verify Dockerfiles
- verify `docker-compose.yml`
- make sure all required files are committed
- verify environment variables

### ChromaDB connection issue
Make sure the API service points to:

```env
CHROMA_HOST=chroma-db
CHROMA_PORT=8000
```

### Memory issues
Increase resource limits in your compose configuration if needed.

### Port conflicts
Let Dokploy manage public exposure where possible instead of hard-coding conflicting ports unnecessarily.

## Security Notes

- keep API keys in Dokploy environment variables
- avoid committing secrets to the repository
- restrict internal-only services such as ChromaDB where possible
- use HTTPS for public endpoints

## Backup Notes

Before making major infrastructure changes, back up any persisted vector database data and keep your deployment configuration versioned.

## Checklist

- [ ] repository connected
- [ ] Docker Compose file selected
- [ ] required environment variables added
- [ ] deployment completed successfully
- [ ] health endpoints responding
- [ ] API docs accessible
- [ ] SSL/domain configuration verified
