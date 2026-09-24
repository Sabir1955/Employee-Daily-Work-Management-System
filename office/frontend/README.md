# Office Portal frontend

React/Vite frontend for the Flask API in the parent directory.

## Run locally

1. Start the Flask API from `E:\office\backend` (it listens on `http://localhost:8000`):

   ```powershell
   .\venv\Scripts\python.exe app.py
   ```

2. Install and start the frontend:

   ```powershell
   cd E:\office\backend\frontend
   npm install
   npm run dev
   ```

Vite proxies `/api` requests to the Flask server and Axios sends credentials so the Flask session cookie is retained. Set `VITE_API_URL` when the API is hosted elsewhere.
