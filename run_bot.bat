@echo off
cd /d "C:\Users\Ozan\Desktop\binance-spot-bot"
echo ------------------------------ >> bot_output.log
echo %date% %time% >> bot_output.log
"C:\Users\Ozan\Desktop\binance-spot-bot\.venv\Scripts\python.exe" "C:\Users\Ozan\Desktop\binance-spot-bot\main.py" >> bot_output.log 2>&1