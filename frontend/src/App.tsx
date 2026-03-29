import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import {
  HomePage,
  SubmissionPage,
  ResultsPage,
  SourcesPage,
  StatsPage,
  DatasetsPage,
  EducationPage,
  FeedbackPage,
  AboutPage,
  AdminPage,
  APIPage
} from './pages'

function App() {
  const navigationItems = [
    { path: '/', label: 'Home' },
    { path: '/submission', label: 'Submission' },
    { path: '/results', label: 'Results' },
    { path: '/sources', label: 'Sources' },
    { path: '/statistics', label: 'Stats' },
    { path: '/datasets', label: 'Datasets' },
    { path: '/education', label: 'Education' },
    { path: '/feedback', label: 'Feedback' },
    { path: '/about', label: 'About' },
    { path: '/admin', label: 'Admin' },
    { path: '/api', label: 'API' }
  ]

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <header className="bg-white border-b border-slate-200 shadow-sm">
          <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-6 sm:px-6 lg:px-8 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 className="text-3xl font-bold">Fake News Guard</h1>
              <p className="mt-1 text-slate-600">A unified dashboard for detection, analytics, datasets, and transparency.</p>
            </div>
            <nav className="flex flex-wrap items-center gap-2">
              {navigationItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `rounded-full px-4 py-2 text-sm font-medium transition ${
                      isActive ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/submission" element={<SubmissionPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/sources" element={<SourcesPage />} />
            <Route path="/statistics" element={<StatsPage />} />
            <Route path="/datasets" element={<DatasetsPage />} />
            <Route path="/education" element={<EducationPage />} />
            <Route path="/feedback" element={<FeedbackPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/api" element={<APIPage />} />
          </Routes>
        </main>

        <footer className="border-t border-slate-200 bg-white py-6">
          <div className="mx-auto max-w-7xl px-4 text-center text-sm text-slate-500 sm:px-6 lg:px-8">
            Frontend and backend are unified through the `/api` proxy. Backend is served by Flask and frontend by Vite.
          </div>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App
