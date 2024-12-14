# Step 1: Create a virtual environment named "venv"
python -m venv venv

# Step 2: Activate the virtual environment
source venv/bin/activate

git clone https://github.com/BoxOfCereal/bs-bot-python

cd bs-bot-python
# Step 3: Install dependencies from the "requirements.txt" file
pip install -r requirements.txt

# Step 4: Run the bot
python ./bots/math-cron-bot.py