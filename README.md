# Pendências System - Scheduler App

Automated task scheduler for executing pendências queries daily at **19:39**.

## New Features (Latest Update)

- 🕰️ **Updated schedule time**: Now executes at 19:39 daily
- 🔍 **Enhanced monitoring**: Status logs every 5 minutes  
- 🧪 **Test script**: Immediate execution testing with `test_scheduler.py`
- 🛡️ **Robust error handling**: Better connection testing and error recovery
- 📊 **Detailed logging**: Complete execution metrics and debug info

## Quick Test

Test the scheduler immediately without waiting for scheduled time:
```bash
python test_scheduler.py
```

## User Configuration

Configure the user ID for history records:
```bash
python config_user.py
```
This will prompt you to set the correct user ID that will be recorded in `amm_histPendencias` table.

## Deployment on EasyPanel

### 1. Create New Service
- Service Type: **Application**
- Name: `pendencias-scheduler`
- Source: Upload this `scheduler-app` folder

### 2. Environment Variables
```
DB_SERVER=your-database-server
DB_NAME=your-database-name  
DB_USER=your-database-user
DB_PASSWORD=your-database-password
OUTPUT_DIR=/app/output
LOG_LEVEL=INFO
USER_ID=1
```
⚠️ **Importante**: Configure `USER_ID` com o ID real do usuário que executará as consultas.

### 3. Resources
- **Memory**: 512MB (minimum)
- **CPU**: 0.5 cores (minimum)
- **Storage**: 1GB for logs and output files

### 4. Features
- ✅ Daily execution at **19:39**
- ✅ Automatic database query execution  
- ✅ Advanced logging and error handling
- ✅ Health monitoring with periodic status updates
- ✅ Connection testing before execution
- ✅ Persistent storage for logs
- ✅ Immediate test execution capability

### 5. Monitoring & Logs
- **Application logs**: `/app/scheduler.log`
- **System logs**: Available in EasyPanel dashboard
- **Status updates**: Every 5 minutes in logs
- **Execution metrics**: Success rate, query count, completion time

### 6. Troubleshooting
If scheduler loads records but doesn't complete execution:
1. Check connection stability
2. Run test script to identify bottlenecks  
3. Review detailed logs for specific error points
4. Verify database query timeouts and permissions