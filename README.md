# didweplay.lol

`didweplay.lol` is a League of Legends matchup checker. Enter two Riot IDs in the format `Name#Tag`, pick the Riot routing region, and the app scans Riot match history to find games where those two players appeared together. When matches are found, the site shows shared-game totals, whether they were teammates or opponents, per-player win counts, and side-by-side match stats.

The project is split into:

- `frontend/`: a Vue 3 + Vite client
- `backend/`: a FastAPI service that talks to the Riot API and streams progress/results back to the UI

## Local setup

### Prerequisites

- Node.js 20+ and npm
- Python 3.11+
- A Riot developer API key

### 1. Configure the backend

Create `backend/.env` with:

```env
RIOT_API_KEY=your_riot_api_key_here
```

Install Python dependencies:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the API server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at [http://localhost:8000](http://localhost:8000).

### 2. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite will start the frontend at [http://localhost:5173](http://localhost:5173).

## How local development works

- The frontend sends matchup requests to `http://localhost:8000/api/check`.
- The backend calls Riot's Account API and Match V5 API.
- Progress is streamed back to the browser with server-sent events so the UI can update while the scan is running.
- Match payloads are cached under `backend/.cache/matches/`.

## Notes

- Riot IDs must include the tagline, for example `ExamplePlayer#EUW`.
- The backend currently allows CORS from `http://localhost:5173`, which matches the default Vite dev server.
- For production on `didweplay.lol`, you will need a deployed backend plus the correct production API base URL and CORS origin configuration.

## License

This project is released under the DoWhatEveryTheFuckYouWant License.
