# EdgeInfer UI - React Frontend

A modern, responsive React UI for EdgeInfer's AI model deployment system.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **Lucide React** - Icons
- **Axios** - HTTP client

## Features

- 📤 Drag-and-drop model upload
- 🎯 Interactive hardware selection
- ⚙️ Optimization level configuration
- 📊 Real-time analysis display
- 📈 Performance metrics visualization
- 💾 Code and report download
- 🌐 Responsive design
- 🎨 Modern UI components

## Getting Started

### Installation

```bash
cd client
npm install
```

### Development

```bash
npm run dev
```

Runs on `http://localhost:3000`

### Building

```bash
npm run build
```

## Project Structure

```
client/
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── types/          # TypeScript types
│   ├── styles/         # CSS files
│   ├── App.tsx         # Main app component
│   └── main.tsx        # Entry point
├── index.html
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── tsconfig.json
```

## Components

- **Header** - Navigation and branding
- **ModelUpload** - File upload with drag & drop
- **HardwareSelector** - Interactive hardware selection
- **OptimizationSelector** - Optimization level chooser
- **ResultsDisplay** - Performance metrics visualization

## API Integration

Connects to Flask backend at `http://localhost:5000/api`

Endpoints:
- `GET /hardware-targets` - Get available hardware
- `POST /analyze` - Analyze model
- `POST /optimize` - Generate optimization strategy
- `POST /generate-code` - Generate inference code
- `POST /benchmark` - Benchmark performance

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```bash
docker build -t edgeinfer-ui .
docker run -p 3000:3000 edgeinfer-ui
```

## Environment Variables

Create `.env.local`:

```
REACT_APP_API_URL=http://localhost:5000/api
```

## Contributing

Follow the existing code style and component patterns.

## License

MIT
