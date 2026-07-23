# Local Backend Deployment with ngrok

## Prerequisites
- Python 3.10+
- Node.js 18+
- ngrok installed and authenticated

## Quick Start

### 1. Start Backend Service
```bash
# Windows
.\scripts\start-backend.ps1

# Linux/Mac
./scripts/start-backend.sh
```

### 2. Start ngrok Tunnel
```bash
# Windows
.\scripts\start-ngrok.ps1

# Linux/Mac
./scripts/start-ngrok.sh
```

### 3. Update Frontend Configuration
Edit `.env.production` and set `VITE_API_BASE_URL` to your ngrok URL.

### 4. Start Frontend
```bash
npm run dev
```

### 5. Access Application
Open http://localhost:5000 in your browser.

## Production Deployment

### Vercel Deployment
1. Push code to GitHub repository
2. Connect repository to Vercel
3. Set environment variable `VITE_API_BASE_URL` to your ngrok URL
4. Deploy

## Long-term Considerations
- For permanent deployment, consider a cloud backend solution
- ngrok free tier has limitations (session limits, URL rotation)
- For production use, consider ngrok paid plans or alternative solutions
