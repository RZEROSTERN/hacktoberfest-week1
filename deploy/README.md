# Deploying

The live demo runs **Sun Oct 4 – Wed Oct 7, 2026** (3 days) to keep GPU costs bounded.
After that the GPU droplet is destroyed and the app stays in the repo for anyone to run.

```
phone ──HTTPS──▶ Render: paperwork-web (Nuxt) ──private network──▶ Render: paperwork-api (FastAPI + Whisper, SQLite on disk)
                                                                         │
                                                                   HTTPS + bearer token
                                                                         ▼
                                                     DigitalOcean GPU Droplet: Caddy ──▶ Ollama (Gemma 4 e4b)
```

## 1. GPU droplet (DigitalOcean)

1. Create a GPU Droplet: **NVIDIA RTX 4000 Ada** (20 GB VRAM, $0.76/h at the time of writing),
   with the **AI/ML-ready** Ubuntu image so NVIDIA drivers are preinstalled. Add your SSH key.
2. Copy and run the setup script:

   ```bash
   scp deploy/gpu-droplet/setup.sh root@<droplet-ip>:
   ssh root@<droplet-ip> "OLLAMA_TOKEN=$(openssl rand -hex 32 | tee /dev/stderr) bash setup.sh"
   ```

   Save the token it prints. The script installs Ollama (bound to localhost), pulls
   `gemma4:e4b`, and puts Caddy in front with automatic HTTPS on `<ip-with-dashes>.sslip.io`.
   Requests without `Authorization: Bearer <token>` get 401.

## 2. Render (web + API)

1. In Render: **New → Blueprint**, pick this repository. Render reads `render.yaml` and deploys
   from `master`.
2. When prompted, set on `paperwork-api`:
   - `ACCESS_CODE`: the family code (the web service copies it automatically)
   - `OLLAMA_BASE_URL`: `https://<ip-with-dashes>.sslip.io` (printed by the setup script)
   - `OLLAMA_API_KEY`: the token from step 1
3. Open the `paperwork-web` URL, enter the family code, take a photo.

The first voice question after a deploy downloads the Whisper weights (~460 MB) to the disk.

## 3. Tear down (Wed Oct 7, 2026)

Destroy the droplet in DigitalOcean (billing stops) and suspend both Render services.
