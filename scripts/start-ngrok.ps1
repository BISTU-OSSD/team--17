# Start ngrok tunnel to expose local backend
Write-Host "Starting ngrok tunnel to expose port 8001..."
ngrok start --config ngrok.yml backend
