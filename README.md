

## Running

1. Navigate to the project directory.
2. Activate the virtual environment and run the server.py:
   ```bash
   source venv/bin/activate
   python3 server.py

   # use this line to kill the 7001 process before restart the server
   netstat -ano | findstr :7001
   kill -9 <PID>

