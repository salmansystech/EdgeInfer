# EdgeInfer UI - React Frontend

A responsive React UI for EdgeInfer's AI model deployment assistant.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Vite** - Dev server and build tool
- **Lucide React** - Icons
- **Axios** - HTTP client

## Features

- 📤 Drag-and-drop model upload
- 🎯 Interactive hardware selection
- ⚙️ Optimization level configuration (conservative, balanced, aggressive)
- 📊 Estimated size, latency, power and accuracy after optimization
- 🔍 Model analysis and optimization plan from the LLM
- 💻 On-demand C/C++ inference code generation
- 💾 Download each result as Markdown
- ⚠️ Clear error messages when the backend or LLM call fails

## Getting Started

The UI needs the Flask backend running. From the project root:

```bash
python server.py   # http://localhost:5000
```

Then, in this folder:

```bash
npm install
npm run dev        # http://localhost:3000
```

In development, Vite proxies `/api` requests to `http://localhost:5000`, so no extra configuration is needed.

### Building

```bash
npm run build      # type-checks with tsc, then builds to dist/
npm run preview    # serves the build on http://localhost:3000
```

## Project Structure

```
client/
├── src/
│   ├── components/     # React components
│   ├── services/       # API client (api.ts)
│   ├── types/          # TypeScript types
│   ├── styles/         # Tailwind CSS
│   ├── App.tsx         # Main app component and workflow
│   ├── main.tsx        # Entry point
│   └── vite-env.d.ts   # Vite environment variable types
├── index.html
├── package.json
├── tailwind.config.js
├── vite.config.ts      # Dev/preview server and /api proxy
└── tsconfig.json
```

## Components

- **Header** - Branding
- **ModelUpload** - File upload with drag & drop
- **HardwareSelector** - Device selection with RAM, Flash and CPU specs
- **OptimizationSelector** - Optimization level chooser
- **ResultsDisplay** - Estimated performance metrics and deployment status
- **AgentOutput** - LLM output panel (analysis, plan, code) with loading state and download

## API Integration

All requests go to `/api` (or `VITE_API_URL` if set):

- `GET /hardware-targets` - Available hardware
- `POST /analyze` - Model analysis
- `POST /optimize` - Optimization strategy
- `POST /generate-code` - Inference code
- `POST /benchmark` - Performance estimate

## Environment Variables

| Variable | Where | Purpose |
|---|---|---|
| `VITE_API_URL` | `.env.local` | Call the API at a different URL instead of `/api` (e.g. `http://localhost:5000/api`). Applied at build time. |
| `API_PROXY_TARGET` | shell / Docker | Where the dev and preview servers forward `/api` (default `http://localhost:5000`). |

## Docker

The easiest way is Docker Compose from the project root, which runs the backend and UI together:

```bash
docker compose up --build
```

## License

MIT
