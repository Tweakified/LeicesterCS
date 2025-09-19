# LeicesterCS Discord Bot

A custom Discord bot for the Leicester Computer Science Society, providing verification, role assignment, tutorials, and more.

## Features

- **Email Verification:** Ensures only university students can write messages on the server.
- **Minecraft Verification:** Handles the LeicesterMC whitelist, ensuring only students/friends of can access our Minecraft server.
- **Role Assignment:** Self-assign roles for year, pronouns, and notifications.
- **Tutorials:** Quick access to module specific resources.
- **Rules Management:** Syncs server rules from Trello.
- **Social Links:** Easy access to official society channels.
- **Status & Uptime:** Bot status and uptime tracking.

## Setup

Follow these steps to get the project running locally:

1. **Fork this repository**
   Click the **Fork** button on the top right of this page to create your own copy.

2. **Clone your fork**
   Replace `<your-username>` with your GitHub username:

   ```bash
   git clone https://github.com/<your-username>/LeicesterCS.git
   cd LeicesterCS
   ```

3. **(Optional but recommended) Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   Copy the example file and fill in your own values:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` to include your own env vars (API keys, tokens, etc.).
   LeicesterCS Trello: https://trello.com/b/VMehvbV5/leicester-cs

7. **Run the project**

    ```bash
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
- **data/modules.json** — Resources for each university module.
- **tests/unit/** — Unit tests for the bot's functionality.
- **tests/parallel/** — Tests for checking that an old and new version both produce the same output.
- **requirements.txt** — Python dependencies.
- **Dockerfile & docker-compose.yaml** — Containerisation support.

## Contributing

Pull requests are welcome! Before opening a PR, Create a feature branch:

    git checkout -b feature/my-feature

Before commiting, run formatting and linting checks (using ruff):

    pip install ruff
    python -m ruff check
    python -m ruff format

Commit & push your changes:

    git commit -m "Add my feature"
    git push origin feature/my-feature
Open a Pull Request!

## Testing

To run the test suite first install the required dependencies:

    pip install -r tests/requirements.txt

Then execute the tests using pytest:

    pytest -v

Parallel tests (i.e., comparing an old version against a newer version) are run manually via GitHub Actions (see `.github/workflows/`). These may be used to verify that code refactoring doesn't change the output. 

## License
This project is licensed under the Apache License 2.0. See LICENSE for details.
