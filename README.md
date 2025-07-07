# Buda Portfolio API

A minimal FastAPI service that calculates the total value of a cryptocurrency portfolio in a given fiat currency, fetching rates from the Buda API.  
Interactive docs are available at:



## Prerequisites

• Python 3.10 or higher  
• pip

## 1. Clone & Prepare

```bash
git clone https://github.com/your-username/BudaTarea.git
cd BudaTarea
```

## 2. Install Dependencies

Install uv package manager:

```bash
pip install uv
```

## 3. Run Server

To tun server on port 5001

```bash
uv run uvicorn server.main:app --host 0.0.0.0 --port 5001
```

## 4. Run Tests

Run Tests

```bash
uv run -m unittest tests/test_root.py -v
```

# Extra 


## Try the remote site:
on https://postulacionbuda.onrender.com/

```bash
curl --location 'https://postulacionbuda.onrender.com/' \
--header 'Content-Type: application/json' \
--data '{
	"portfolio": {
		"BTC": 0.1,
		"ETH": 2.0,
		"USDT": 1000
	},
	"fiat_currency": "CLP"
}
'
```

**For the OpenAPI Schema** send a get request to https://postulacionbuda.onrender.com/docs