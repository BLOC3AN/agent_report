# 🐳 Docker Deployment Guide

## 🚀 Quick Start

### **1. Prerequisites:**
- Docker & Docker Compose installed
- Slack Bot Token & User ID
- Google API Key & Gemini API Key

### **2. Setup Environment:**
```bash
# Create .env file in project root with your credentials
cp .env.example .env
nano .env
```

### **3. Required Environment Variables:**
```bash
# Database (MongoDB Atlas or local)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/agent_reports

# Slack Integration
SLACK_BOT_TOKEN=xoxb-your-actual-bot-token
SLACK_USER_ID=U1234567890

# API Keys
GOOGLE_API_KEY=your-google-api-key
GEMINI_API_KEY=your-gemini-api-key

# Google Sheets URL
DEFAULT_SHEET_URL=your-google-sheets-url
```

### **4. Deploy:**
```bash
# Simple deploy (from project root)
./deploy.sh

# Or manual
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 📊 **Services Included:**

### **1. Agent Report Service:**
- **Port**: 5000
- **Features**: 
  - ✅ Automated scheduler (10:00, 12:00, 15:00)
  - ✅ Slack notifications & reminders
  - ✅ Google Sheets integration
  - ✅ MongoDB storage
  - ✅ State persistence

### **2. MongoDB Database:**
- **Port**: 27017
- **Features**:
  - ✅ Persistent data storage
  - ✅ Auto-initialization
  - ✅ Volume mounting

## 🔧 **Configuration:**

### **Scheduler Settings:**
```yaml
environment:
  - SCHEDULER_ENABLED=true
  - SCHEDULER_TIMEZONE=Asia/Ho_Chi_Minh
  - SCHEDULER_CHECK_TIMES=10:00,12:00,15:00
  - SCHEDULER_MAX_REMINDERS=3
```

### **Data Persistence:**
```yaml
volumes:
  - scheduler_data:/app/data  # Scheduler state
  - ./logs:/app/logs         # Application logs
  - mongodb_data:/data/db    # MongoDB data
```

## 📱 **API Endpoints:**

### **Health Check:**
```bash
curl http://localhost:5000/health
```

### **Scheduler Status:**
```bash
curl http://localhost:5000/scheduler/status
```

### **Manual Report Generation:**
```bash
curl -X POST http://localhost:5000/report \
  -H "Content-Type: application/json" \
  -d '{
    "sheet_url": "your-google-sheets-url",
    "additional_context": "Manual report generation"
  }'
```

### **Manual Scheduler Trigger:**
```bash
curl -X POST http://localhost:5000/scheduler/trigger
```

## 🔍 **Monitoring:**

### **View Logs:**
```bash
# All services
docker-compose -f deployment/docker-compose.yml logs -f

# Specific service
docker-compose -f deployment/docker-compose.yml logs -f agent-report
docker-compose -f deployment/docker-compose.yml logs -f mongodb
```

### **Check Container Status:**
```bash
docker-compose -f deployment/docker-compose.yml ps
```

### **Access MongoDB:**
```bash
# Connect to MongoDB container
docker exec -it agent-report-mongodb mongosh

# Use database
use agent_reports

# Check collections
show collections

# View recent reports
db.chat_history.find().sort({timestamp: -1}).limit(5)
```

## 🛠️ **Troubleshooting:**

### **Common Issues:**

#### **1. Scheduler not working:**
```bash
# Check scheduler status
curl http://localhost:5000/scheduler/status

# Check logs for scheduler errors
docker-compose logs agent-report | grep -i scheduler
```

#### **2. Slack notifications failing:**
```bash
# Test Slack connection
curl http://localhost:5000/test-slack

# Check Slack credentials in .env file
```

#### **3. MongoDB connection issues:**
```bash
# Check MongoDB container
docker-compose ps mongodb

# Check MongoDB logs
docker-compose logs mongodb
```

### **Restart Services:**
```bash
# Restart all services
docker-compose -f deployment/docker-compose.yml restart

# Restart specific service
docker-compose -f deployment/docker-compose.yml restart agent-report
```

### **Clean Restart:**
```bash
# Stop and remove containers
docker-compose -f deployment/docker-compose.yml down

# Remove volumes (WARNING: This deletes all data)
docker-compose -f deployment/docker-compose.yml down -v

# Rebuild and start
docker-compose -f deployment/docker-compose.yml up -d --build
```

## 🚀 **Production Deployment:**

### **For AWS/Cloud deployment:**
1. Update `DEFAULT_SHEET_URL` with your actual Google Sheets URL
2. Use external MongoDB (MongoDB Atlas) instead of container
3. Set up proper SSL/TLS termination
4. Configure log aggregation
5. Set up monitoring and alerts

### **Environment Variables for Production:**
```bash
# Use external MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/agent_reports

# Disable debug mode
DEBUG=false
LOG_LEVEL=INFO

# Production Slack settings
SLACK_BOT_TOKEN=xoxb-production-token
SLACK_USER_ID=U-production-user-id
```

## 📈 **Scaling:**

### **Multiple Instances:**
```yaml
# In docker-compose.yml
agent-report:
  deploy:
    replicas: 2
  # Note: Only one instance should run scheduler
```

### **Load Balancer:**
```yaml
# Add nginx load balancer
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
```

## 🎯 **Success Indicators:**

✅ **Scheduler running**: Check `/scheduler/status`  
✅ **MongoDB connected**: Check `/health`  
✅ **Slack working**: Check `/test-slack`  
✅ **Reports generating**: Check logs for "Report processing completed"  
✅ **State persisting**: Check `scheduler_data` volume  

**Your automated report system is now running! 🎉**
