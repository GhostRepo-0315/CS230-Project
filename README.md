

## Running

1. Navigate to the project directory.
2. Activate the virtual environment and run the server.py:
   ```bash
   source venv/bin/activate
   python3 server.py

   # use thse two lines to kill all processes occupy 7001 port before restart the server
   sudo lsof -i :7001
   kill -9 <PID>

