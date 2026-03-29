# Fake News Detector - Modern Frontend

A modern, responsive React frontend for the Fake News Detection API built with cutting-edge web technologies.

## 🚀 Technologies Used

- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type-safe JavaScript for better development experience
- **Vite** - Lightning-fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful, customizable icons
- **Axios** - HTTP client for API calls

## ✨ Features

- **Modern UI/UX** - Clean, professional design with smooth animations
- **Responsive Design** - Works perfectly on all devices
- **Real-time Analysis** - Instant feedback with loading states
- **Confidence Visualization** - Visual confidence meter
- **Type Safety** - Full TypeScript support
- **Fast Development** - Hot reload with Vite
- **API Integration** - Seamless connection to Flask backend

## 🛠️ Setup & Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   The app will be available at `http://localhost:5173`

## 🔧 Development

- **Build for production:**
  ```bash
  npm run build
  ```

- **Preview production build:**
  ```bash
  npm run preview
  ```

- **Lint code:**
  ```bash
  npm run lint
  ```

## 🔌 API Integration

The frontend automatically proxies API calls to the Flask backend running on port 5000. Make sure the backend is running before using the frontend.

API endpoints used:
- `POST /api/predict` - News analysis

## 📱 Responsive Design

The app is fully responsive and optimized for:
- Desktop computers
- Tablets
- Mobile phones

## 🎨 Customization

- **Colors:** Modify Tailwind config in `tailwind.config.js`
- **Components:** Update styles in `src/index.css`
- **Icons:** Replace Lucide icons in `App.tsx`
- **API:** Change proxy settings in `vite.config.ts`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run linting: `npm run lint`
5. Test thoroughly
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.