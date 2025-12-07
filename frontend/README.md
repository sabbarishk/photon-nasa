# Photon Frontend

Production-quality React frontend for Photon - NASA Data Query & Workflow Generator.

## Features

- 🔍 **Natural Language Search** - Find NASA datasets using plain English
- 📊 **Workflow Generator** - Automatically create Jupyter notebooks
- 🎨 **NASA-Themed Design** - Beautiful, professional UI with NASA branding
- 📱 **Responsive** - Works on desktop, tablet, and mobile
- ⚡ **Fast** - Built with Vite for lightning-fast development

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Next-generation frontend tooling
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **React Router** - Client-side routing
- **Lucide React** - Beautiful icon library

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Backend server running at http://localhost:8000

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will open at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The optimized build will be in the `dist/` folder.

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Navbar.jsx       # Top navigation
│   │   ├── Hero.jsx         # Landing hero section
│   │   ├── Search.jsx       # Dataset search
│   │   ├── WorkflowGenerator.jsx  # Notebook generator
│   │   └── Footer.jsx       # Footer
│   ├── services/
│   │   └── api.js           # API client
│   ├── App.jsx              # Main app component
│   ├── main.jsx             # Entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies
├── vite.config.js           # Vite configuration
└── tailwind.config.js       # Tailwind configuration
```

## API Integration

The frontend connects to the backend API at `http://localhost:8000` by default.

### Endpoints Used

- `GET /health` - Health check
- `POST /query/` - Search datasets
- `POST /workflow/generate` - Generate notebooks

### Environment Variables

Create a `.env` file to customize the API URL:

```env
VITE_API_URL=http://localhost:8000
```

## Design System

### Colors

- **NASA Blue**: `#0B3D91` - Primary brand color
- **NASA Red**: `#FC3D21` - Accent color
- **NASA Dark**: `#0A1828` - Background
- **NASA Light**: `#F5F7FA` - Text

### Typography

- **Font**: Inter (from Google Fonts)
- **Sizes**: Responsive, from mobile to desktop

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Adding New Components

1. Create component in `src/components/`
2. Import in `App.jsx` or parent component
3. Add routing if needed in `App.jsx`

## Deployment

### Option 1: Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Option 2: Netlify

```bash
npm run build
# Drag and drop dist/ folder to Netlify
```

### Option 3: GitHub Pages

```bash
npm run build
# Copy dist/ to gh-pages branch
```

## Troubleshooting

**CORS Errors**
- Make sure backend has CORS enabled
- Check that API_URL matches your backend

**Build Errors**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node -v` (should be 16+)

**Styling Issues**
- Run `npm install tailwindcss postcss autoprefixer`
- Check `tailwind.config.js` content paths

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Open source - see LICENSE file

## Support

- Documentation: `/photon/docs/`
- Issues: GitHub Issues
- Contact: [Your contact info]
