# Website-Scrapper

## Deployment

### Production Deployment Options

#### Option 1: Railway (Recommended - Easy)

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy**:
   ```bash
   railway init
   railway up
   ```

3. **Set Environment Variables** (if needed):
   - Go to Railway dashboard → Variables
   - Add any required environment variables

4. **Your app will be live at**: `https://your-app.railway.app`

#### Option 2: Render

1. **Connect Repository**:
   - Go to https://render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure**:
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
   - **Plan**: Free tier available

3. **Deploy**: Render will automatically deploy on every push to main branch

#### Option 3: Heroku

1. **Install Heroku CLI**:
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**:
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Create `Procfile`**:
   ```
   web: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

4. **Create `runtime.txt`**:
   ```
   python-3.11.0
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

6. **Install Playwright** (if needed):
   ```bash
   heroku run playwright install chromium
   ```

#### Option 4: DigitalOcean App Platform

1. **Connect Repository**:
   - Go to https://cloud.digitalocean.com/apps
   - Click "Create App" → "GitHub"
   - Select your repository

2. **Configure**:
   - **Type**: Web Service
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Run Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add any required vars

3. **Deploy**: DigitalOcean will handle the rest

#### Option 5: VPS Deployment (Ubuntu/Debian)

1. **SSH into your server**:
   ```bash
   ssh user@your-server-ip
   ```

2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx
   ```

3. **Clone and setup**:
   ```bash
   git clone https://github.com/Vaibhavjindal10/your-repo.git
   cd your-repo
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Create systemd service** (`/etc/systemd/system/scraper.service`):
   ```ini
   [Unit]
   Description=Lyftr AI Scraper
   After=network.target

   [Service]
   User=your-user
   WorkingDirectory=/path/to/your-repo
   Environment="PATH=/path/to/your-repo/venv/bin"
   ExecStart=/path/to/your-repo/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. **Start service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable scraper
   sudo systemctl start scraper
   ```

6. **Configure Nginx** (`/etc/nginx/sites-available/scraper`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

7. **Enable site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/scraper /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

#### Option 6: Docker Deployment

1. **Create `Dockerfile`**:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       wget \
       gnupg \
       && rm -rf /var/lib/apt/lists/*

   # Install Playwright dependencies
   RUN apt-get update && apt-get install -y \
       libnss3 \
       libatk1.0-0 \
       libatk-bridge2.0-0 \
       libcups2 \
       libdrm2 \
       libxkbcommon0 \
       libxcomposite1 \
       libxdamage1 \
       libxfixes3 \
       libxrandr2 \
       libgbm1 \
       libasound2 \
       && rm -rf /var/lib/apt/lists/*

   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Install Playwright browsers
   RUN playwright install chromium
   RUN playwright install-deps chromium

   # Copy application code
   COPY . .

   # Expose port
   EXPOSE 8000

   # Run the application
   CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Create `.dockerignore`**:
   ```
   __pycache__
   *.pyc
   venv/
   .git
   .gitignore
   *.md
   ```

3. **Build and run**:
   ```bash
   docker build -t lyftr-scraper .
   docker run -p 8000:8000 lyftr-scraper
   ```

4. **Docker Compose** (`docker-compose.yml`):
   ```yaml
   version: '3.8'

   services:
     scraper:
       build: .
       ports:
         - "8000:8000"
       restart: unless-stopped
       environment:
         - PORT=8000
   ```

   Run with: `docker-compose up -d`

### Environment Variables

Create a `.env` file for local development (optional):

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Optional: Rate limiting
MAX_REQUESTS_PER_MINUTE=60

# Optional: Timeout settings
REQUEST_TIMEOUT=30
PLAYWRIGHT_TIMEOUT=60000
```

### Production Considerations

1. **Security**:
   - Add CORS middleware if needed
   - Implement rate limiting
   - Add authentication for production use
   - Validate and sanitize input URLs
   - Use HTTPS (Let's Encrypt for free SSL)

2. **Performance**:
   - Use a production ASGI server (Gunicorn with Uvicorn workers)
   - Enable caching for frequently scraped URLs
   - Use connection pooling
   - Consider Redis for session management

3. **Monitoring**:
   - Add logging (use Python's `logging` module)
   - Set up health checks
   - Monitor resource usage
   - Track error rates

4. **Scaling**:
   - Use a load balancer for multiple instances
   - Consider message queues for async scraping
   - Use database for storing results
   - Implement caching layer

### Production Server Command

For production, use Gunicorn with Uvicorn workers:

```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Or with more configuration:

```bash
gunicorn app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

## Dependencies

- `fastapi==0.104.1`: Web framework
- `uvicorn[standard]==0.24.0`: ASGI server
- `requests==2.31.0`: HTTP client for static scraping
- `beautifulsoup4==4.12.2`: HTML parser
- `playwright==1.40.0`: Browser automation for JS rendering
- `python-multipart==0.0.6`: Form data handling
- `jinja2==3.1.2`: Template engine for frontend

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Find process using port 8000
   lsof -i :8000  # Mac/Linux
   netstat -ano | findstr :8000  # Windows
   # Kill the process or use a different port
   ```

2. **Playwright not working**:
   ```bash
   playwright install chromium
   playwright install-deps chromium
   ```

3. **Import errors**:
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

4. **Memory issues with large pages**:
   - Increase timeout settings
   - Reduce scroll depth
   - Process pages in chunks
