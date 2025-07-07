A minimal Flask-based service that calculates the total value of a cryptocurrency portfolio in a given fiat currency, fetching rates from the Buda API.

Prerequisites

• Python 3.8 or higher
• pip

1. a) Clone this repo:


	git clone https://github.com/your-username/BudaTarea.git
	cd BudaTarea



1. b) 
(Optional) Create and activate a virtual environment:


	python -m venv .venv
	source .venv/bin/activate   # macOS/Linux
	.venv\Scripts\activate      # Windows



1. c)
Install project dependencies:


	pip install -r requirements.txt




2. Run the Server

From the project root, start the Flask app via, it listens on http://127.0.0.1:5001:

	python -m server.main


3. Test the API

To run it:

	python -m unittest tests/test_root.py -v
