# NexusAI - Start all services
$root = "C:\shared\projects\nexusai"

Write-Host "Starting NexusAI..." -ForegroundColor Cyan

# Start backend
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; conda activate aitools; python run.py" -WindowStyle Normal

Start-Sleep 3

# Start frontend
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev" -WindowStyle Normal

Start-Sleep 3

Write-Host ""
Write-Host "NexusAI is running!" -ForegroundColor Green
Write-Host "  Web UI  : http://localhost:3000" -ForegroundColor White  
Write-Host "  API     : http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "CLI usage:" -ForegroundColor Yellow
Write-Host "  python $root\cli\nexus.py chat" -ForegroundColor Gray
Write-Host "  python $root\cli\nexus.py run 'write a python script to sort files'" -ForegroundColor Gray
Write-Host "  python $root\cli\nexus.py models" -ForegroundColor Gray
Write-Host "  python $root\cli\nexus.py cost" -ForegroundColor Gray
