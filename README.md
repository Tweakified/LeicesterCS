# LeicesterCS Discord Bot

A custom Discord bot for the Leicester Computer Science Society, providing verification, role assignment, tutorials, and more.

## Features

- **Email Verification:** Ensures only university students can access the server.
- **Role Assignment:** Self-assign roles for year, pronouns, and notifications.
- **Tutorials:** Quick access to module specific resources.
- **Rules Management:** Syncs server rules from Trello.
- **Social Links:** Easy access to official society channels.
- **Status & Uptime:** Bot status and uptime tracking.

## Setup

1. **Fork the repository**

2. **Clone the repository:**
    ```
    git clone <repo-url>
    cd LeicesterCS
    ```

3. **Install dependencies:**
    ```
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**

    Copy .env.example to .env and fill in your Discord token, Mailjet keys, Trello keys, and other relevant keys. Please note only some keys are required for the bot to function.
   LeicesterCS Trello: https://trello.com/b/VMehvbV5/leicester-cs

6. **Run the bot:**
    ```
    python bot.py
    ```
    Or use Docker:
    ```
    docker compose up --build
    ```

## File Structure

- **bot.py** — Main bot entry point.
- **cogs/** — Bot features (verification, tutorials, tasks, etc.).
- **modules/enums.py** — Shared enums and constants.
- **requirements.txt** — Python dependencies.
- **Dockerfile & docker-compose.yaml** — Containerisation support.

## Contributing
Pull requests are welcome! Please follow the Apache 2.0 License.
Please run ruff check and ruff format before pushing your code.
    
    pip install ruff
    python -m ruff check
    python -m ruff format

## License
This project is licensed under the Apache License 2.0. See LICENSE for details.
