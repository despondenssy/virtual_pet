# Virtual Pet

This is a simple web application where you can interact with virtual pets. You can feed them, play with them, and see their mood change based on their energy and satiety levels.

## Technologies Used
- Python
- Django
- HTML/CSS
- PostgreSQL
- Redis (KeyDB)
- Docker / Docker Compose

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/despondenssy/virtual_pet.git
   cd virtual_pet
2. Build and start the application:
   ```bash
   docker compose up --build -d
3. The application will be available at:
    `http://localhost:8080`
4. To view logs:
   ```bash
   docker compose logs -f app


## Usage
- Go to `http://localhost:8080` to interact with your virtual pet.
- You can add, feed, play with, and delete pets.