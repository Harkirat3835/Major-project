import { useEffect, useState } from 'react'
import axios from 'axios'
import { useNavigate, useLocation, Link } from 'react-router-dom'

const apiBase = '/api'

export function HomePage() {
  const [overview, setOverview] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    axios
      .get(`${apiBase}/pages/overview`)
      .then((response) => setOverview(response.data))
      .catch(() => setError('Unable to load overview details.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-10">
      <section className="rounded-[32px] bg-gradient-to-r from-slate-900 via-slate-800 to-sky-700 px-8 py-16 text-white shadow-xl">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-8 lg:grid-cols-[2fr_1fr] lg:items-center">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-sky-300">Trusted AI Verification</p>
              <h1 className="mt-6 text-5xl font-bold leading-tight">Professional Fake News Detection & Media Intelligence</h1>
              <p className="mt-6 max-w-2xl text-lg text-slate-200">Convert uncertain news and social content into clear credibility decisions using advanced analytics, trusted fact-check sources, and modern AI workflows.</p>
              <div className="mt-8 flex flex-col gap-4 sm:flex-row">
                <Link to="/submission" className="inline-flex items-center justify-center rounded-full bg-white px-8 py-3 text-sm font-semibold text-slate-900 shadow-lg transition hover:bg-slate-100">Start Verification</Link>
                <Link to="/api" className="inline-flex items-center justify-center rounded-full border border-white/30 px-8 py-3 text-sm font-semibold text-white transition hover:border-white">View API Docs</Link>
              </div>
            </div>
            <div className="rounded-[32px] bg-slate-950/80 p-8 shadow-2xl">
              <div className="space-y-6">
                <div>
                  <span className="text-sm uppercase tracking-[0.3em] text-sky-300">Intelligence Snapshot</span>
                  <h2 className="mt-3 text-3xl font-semibold">Accurate detection for modern teams</h2>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-3xl bg-slate-900 p-5">
                    <p className="text-sm text-slate-400">Total analyses</p>
                    <p className="mt-3 text-3xl font-semibold text-white">{overview?.overview?.total_analyses ?? '—'}</p>
                  </div>
                  <div className="rounded-3xl bg-slate-900 p-5">
                    <p className="text-sm text-slate-400">Trusted outcomes</p>
                    <p className="mt-3 text-3xl font-semibold text-white">{overview?.overview?.real_news_count ?? '—'}</p>
                  </div>
                </div>
                <div className="rounded-3xl bg-slate-900 p-5">
                  <p className="text-sm text-slate-400">Flagged insights</p>
                  <p className="mt-3 text-3xl font-semibold text-white">{overview?.overview?.fake_news_count ?? '—'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        {[
          { title: 'Verify Fast', description: 'Analyze content in seconds with automated credibility scoring.' },
          { title: 'Learn More', description: 'Access educational resources that explain misinformation detection.' },
          { title: 'Integrate Easily', description: 'Use REST APIs to connect verification into your workflows.' }
        ].map((item) => (
          <div key={item.title} className="rounded-3xl bg-white p-8 shadow-lg">
            <h2 className="text-xl font-semibold">{item.title}</h2>
            <p className="mt-4 text-slate-600">{item.description}</p>
          </div>
        ))}
      </section>

      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <div className="grid gap-8 lg:grid-cols-3">
          <div>
            <h2 className="text-2xl font-semibold">How it works</h2>
            <p className="mt-4 text-slate-600">The platform analyzes submitted content against model predictions, credibility signals, and trusted fact-check sources to produce clear, actionable recommendations.</p>
          </div>
          <div className="space-y-4">
            <div className="rounded-3xl bg-slate-50 p-6">
              <p className="text-sm text-slate-500">Step 1</p>
              <p className="mt-3 font-semibold">Submit an article, link, or post.</p>
            </div>
            <div className="rounded-3xl bg-slate-50 p-6">
              <p className="text-sm text-slate-500">Step 2</p>
              <p className="mt-3 font-semibold">Get AI-assisted credibility feedback.</p>
            </div>
            <div className="rounded-3xl bg-slate-50 p-6">
              <p className="text-sm text-slate-500">Step 3</p>
              <p className="mt-3 font-semibold">Review results and use them responsibly.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export function SubmissionPage() {
  const [inputType, setInputType] = useState<'text' | 'link' | 'social'>('text')
  const [inputValue, setInputValue] = useState('')
  const [status, setStatus] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleAnalyze = async () => {
    if (!inputValue.trim()) {
      setStatus('Please enter content before submitting.')
      return
    }

    setLoading(true)
    setStatus(null)

    try {
      const response = await axios.post(`${apiBase}/analysis/predict`, {
        text: inputValue
      })
      navigate('/results', { state: { result: response.data } })
    } catch (error: any) {
      setStatus(error?.response?.data?.error || 'Unable to analyze content. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-10">
      <section className="rounded-[32px] bg-gradient-to-r from-slate-900 to-sky-700 px-10 py-14 text-white shadow-xl">
        <h1 className="text-4xl font-bold">Submit Content for Verification</h1>
        <p className="mt-4 max-w-2xl text-lg text-slate-100">Submit a news story, URL, or social media post and receive a professionally structured credibility assessment.</p>
      </section>

      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <div className="grid gap-4 md:grid-cols-3">
          <button
            className="rounded-3xl p-5 text-left transition border"
            onClick={() => setInputType('text')}
          >
            <p className="text-sm text-slate-500">Article Text</p>
            <p className="mt-3 font-semibold">Paste your content</p>
          </button>
          <button
            className="rounded-3xl p-5 text-left transition border"
            onClick={() => setInputType('link')}
          >
            <p className="text-sm text-slate-500">News Link</p>
            <p className="mt-3 font-semibold">Analyze any URL</p>
          </button>
          <button
            className="rounded-3xl p-5 text-left transition border"
            onClick={() => setInputType('social')}
          >
            <p className="text-sm text-slate-500">Social Post</p>
            <p className="mt-3 font-semibold">Review social media</p>
          </button>
        </div>

        <div className="mt-8">
          <label className="block text-sm font-semibold text-slate-700 mb-3">
            {inputType === 'text' ? 'Article Content' : inputType === 'link' ? 'Source URL' : 'Social Content'}
          </label>
          <textarea
            className="min-h-[220px] w-full rounded-[28px] border border-slate-300 px-5 py-4 text-slate-900 focus:border-sky-500 focus:outline-none"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={
              inputType === 'text'
                ? 'Paste the news article text here...'
                : inputType === 'link'
                ? 'Paste the URL of the article or post here...'
                : 'Paste the social media content here...'
            }
          />
        </div>

        {status && <div className="mt-6 rounded-3xl bg-rose-50 p-5 text-rose-700">{status}</div>}

        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="inline-flex items-center justify-center rounded-full bg-slate-900 px-8 py-4 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60"
          >
            {loading ? 'Running verification...' : 'Run Verification'}
          </button>
          <p className="text-sm text-slate-500">All submissions are processed securely and used to improve system accuracy.</p>
        </div>
      </section>
    </div>
  )
}

export function ResultsPage() {
  const location = useLocation()
  const result = (location.state as any)?.result

  if (!result) {
    return (
      <div className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-3xl font-bold">Verification Results</h1>
        <p className="mt-4 text-slate-600">Results are displayed after successful content submission.</p>
        <Link className="mt-6 inline-flex rounded-full bg-slate-900 px-6 py-3 text-white" to="/submission">Submit Content</Link>
      </div>
    )
  }

  const isReal = result.prediction === 'Real'
  const badgeClass = isReal ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'

  return (
    <div className="space-y-10">
      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="text-4xl font-bold">Verification Summary</h1>
            <p className="mt-4 max-w-2xl text-slate-600">Precise results, confidence scores, and evidence-based insights for your submission.</p>
          </div>
          <div className="rounded-full px-6 py-4 text-lg font-semibold">
            {result.prediction}
          </div>
        </div>

        <div className="mt-10 grid gap-6 lg:grid-cols-3">
          <div className="rounded-3xl bg-slate-50 p-6">
            <p className="text-sm text-slate-500">Confidence</p>
            <p className="mt-4 text-3xl font-semibold text-slate-900">{result.confidence ? `${(result.confidence * 100).toFixed(1)}%` : 'N/A'}</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-6">
            <p className="text-sm text-slate-500">Analysis ID</p>
            <p className="mt-4 text-3xl font-semibold text-slate-900">{result.analysis_id ?? '—'}</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-6">
            <p className="text-sm text-slate-500">Processing time</p>
            <p className="mt-4 text-3xl font-semibold text-slate-900">{result.processing_time ? `${result.processing_time.toFixed(0)} ms` : 'N/A'}</p>
          </div>
        </div>

        <div className="mt-10 rounded-3xl bg-slate-50 p-8">
          <h2 className="text-2xl font-semibold">Evidence summary</h2>
          {result.reasons?.length ? (
            <ul className="mt-4 list-disc pl-5 space-y-3 text-slate-700">
              {result.reasons.map((reason: string, index: number) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 text-slate-700">No significant deceptive indicators were detected.</p>
          )}
        </div>
      </section>
    </div>
  )
}

export function SourcesPage() {
  const [sources, setSources] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    axios
      .get(`${apiBase}/pages/fact-check-sources`)
      .then((response) => setSources(response.data.sources || []))
      .catch(() => setError('Unable to load trusted sources.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-10">
      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-4xl font-bold">Trusted Verification Partners</h1>
        <p className="mt-4 text-slate-600">Our analysis is supported by reputable fact-check organizations and established verification networks.</p>
      </section>

      {loading ? (
        <div className="rounded-3xl bg-slate-50 p-10 text-slate-600">Loading partner details...</div>
      ) : error ? (
        <div className="rounded-3xl bg-rose-50 p-10 text-rose-700">{error}</div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          {sources.map((source, index) => (
            <div key={index} className="rounded-3xl bg-slate-50 p-8 shadow-sm">
              <h2 className="text-xl font-semibold">{source.name}</h2>
              <p className="mt-4 text-slate-700">{source.description}</p>
              <a className="mt-6 inline-block text-sky-600 hover:underline" href={source.website} target="_blank" rel="noreferrer">Learn more</a>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function StatsPage() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    axios
      .get(`${apiBase}/pages/statistics`)
      .then((response) => setStats(response.data))
      .catch(() => setError('Unable to load analytics data.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-10">
      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-4xl font-bold">Performance Insights</h1>
        <p className="mt-4 text-slate-600">Explore how the detection engine performs across categories and regions.</p>
      </section>

      {loading ? (
        <div className="rounded-3xl bg-slate-50 p-10 text-slate-600">Loading performance insights...</div>
      ) : error ? (
        <div className="rounded-3xl bg-rose-50 p-10 text-rose-700">{error}</div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-3xl bg-white p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Fake vs Real</h2>
            <p className="mt-4 text-slate-700">Real content: {stats.fake_vs_real.real}</p>
            <p className="text-slate-700">Flagged content: {stats.fake_vs_real.fake}</p>
          </div>
          <div className="rounded-3xl bg-white p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Top Categories</h2>
            <ul className="mt-4 list-disc pl-5 text-slate-700 space-y-2">
              {stats.top_categories.map((category: any) => (
                <li key={category.name}>{category.name}: {category.count} alerts</li>
              ))}
            </ul>
          </div>
          <div className="rounded-3xl bg-white p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Regional Signals</h2>
            <ul className="mt-4 list-disc pl-5 text-slate-700 space-y-2">
              {stats.regions.map((region: any) => (
                <li key={region.region}>{region.region}: {region.share}% share</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export function DatasetsPage() {
  const [datasets, setDatasets] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    axios
      .get(`${apiBase}/pages/datasets`)
      .then((response) => setDatasets(response.data))
      .catch(() => setError('Unable to load dataset details.'))
  }, [])

  return (
    <div className="space-y-10">
      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-4xl font-bold">Training Data & Research</h1>
        <p className="mt-4 text-slate-600">Our models are trained using established datasets and refined through responsible evaluation.</p>
      </section>

      {error ? (
        <div className="rounded-3xl bg-rose-50 p-10 text-rose-700">{error}</div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl bg-slate-50 p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Dataset Overview</h2>
            <p className="mt-4 text-slate-700">{datasets?.description ?? 'Curated datasets support model accuracy while preserving user submission privacy.'}</p>
          </div>
          <div className="rounded-3xl bg-white p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Used Resources</h2>
            <ul className="mt-4 list-disc pl-5 text-slate-700 space-y-2">
              {datasets?.datasets?.map((dataset: any) => (
                <li key={dataset.name}><strong>{dataset.name}</strong>: {dataset.summary}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export function EducationPage() {
  const [education, setEducation] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    axios
      .get(`${apiBase}/pages/education`)
      .then((response) => setEducation(response.data.resources || []))
      .catch(() => setError('Unable to load education resources.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-10">
      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-4xl font-bold">Education & Media Literacy</h1>
        <p className="mt-4 text-slate-600">Learn how to detect unreliable information and verify claims with confidence.</p>
      </section>

      {loading ? (
        <div className="rounded-3xl bg-slate-50 p-10 text-slate-600">Loading resources...</div>
      ) : error ? (
        <div className="rounded-3xl bg-rose-50 p-10 text-rose-700">{error}</div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {education.map((item: any, index: number) => (
            <div key={index} className="rounded-3xl bg-slate-50 p-8 shadow-sm">
              <h2 className="text-xl font-semibold">{item.title}</h2>
              <p className="mt-4 text-slate-700">{item.description}</p>
              {item.link && (
                <a className="mt-5 inline-block text-sky-600 hover:underline" href={item.link} target="_blank" rel="noreferrer">Read more</a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function FeedbackPage() {
  const [summary, setSummary] = useState<{ total: number; positive: number; negative: number } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    axios
      .get(`${apiBase}/data/feedback`)
      .then((response) => {
        const entries = response.data || []
        const total = entries.length
        const positive = entries.filter((item: any) => item.is_correct).length
        const negative = total - positive
        setSummary({ total, positive, negative })
      })
      .catch(() => setError('Unable to load community feedback.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-10">
      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-4xl font-bold">Community Confidence</h1>
        <p className="mt-4 text-slate-600">User feedback powers model improvement and helps maintain the platform’s reliability.</p>
      </section>

      {loading ? (
        <div className="rounded-3xl bg-slate-50 p-10 text-slate-600">Calculating feedback metrics...</div>
      ) : error ? (
        <div className="rounded-3xl bg-rose-50 p-10 text-rose-700">{error}</div>
      ) : summary ? (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-3xl bg-white p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Total Reviews</h2>
            <p className="mt-4 text-slate-700">{summary.total}</p>
          </div>
          <div className="rounded-3xl bg-white p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Positive Validation</h2>
            <p className="mt-4 text-slate-700">{summary.positive}</p>
          </div>
          <div className="rounded-3xl bg-white p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Suggested Revisions</h2>
            <p className="mt-4 text-slate-700">{summary.negative}</p>
          </div>
        </div>
      ) : null}
    </div>
  )
}

export function AboutPage() {
  const [about, setAbout] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    axios
      .get(`${apiBase}/pages/about`)
      .then((response) => setAbout(response.data))
      .catch(() => setError('Unable to load company story.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-10">
      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-4xl font-bold">About Fake News Guard</h1>
        <p className="mt-4 text-slate-600">We build intelligent tools that help teams and individuals navigate information with confidence.</p>
      </section>

      {loading ? (
        <div className="rounded-3xl bg-slate-50 p-10 text-slate-600">Loading about details...</div>
      ) : error ? (
        <div className="rounded-3xl bg-rose-50 p-10 text-rose-700">{error}</div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-3xl bg-slate-50 p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Mission</h2>
            <p className="mt-4 text-slate-700">{about?.overview}</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Process</h2>
            <p className="mt-4 text-slate-700">{about?.algorithms}</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Guiding Principles</h2>
            <p className="mt-4 text-slate-700">{about?.limitations}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export function AdminPage() {
  const [flagged, setFlagged] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    axios
      .get(`${apiBase}/admin/flagged`)
      .then((response) => setFlagged(response.data.flagged || []))
      .catch(() => setError('Unable to load flagged content summary.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-10">
      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-4xl font-bold">Administration Overview</h1>
        <p className="mt-4 text-slate-600">Track platform health and review flagged submissions from a clean operational dashboard.</p>
      </section>

      {loading ? (
        <div className="rounded-3xl bg-slate-50 p-10 text-slate-600">Loading admin summary...</div>
      ) : error ? (
        <div className="rounded-3xl bg-rose-50 p-10 text-rose-700">{error}</div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl bg-white p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Flagged Cases</h2>
            <p className="mt-4 text-slate-700">{flagged.length} cases currently marked for review.</p>
          </div>
          <div className="rounded-3xl bg-white p-8 shadow-sm">
            <h2 className="text-xl font-semibold">Team Actions</h2>
            <p className="mt-4 text-slate-700">Review flagged signals, confirm model behavior, and manage updates.</p>
          </div>
        </div>
      )}
    </div>
  )
}

export function APIPage() {
  return (
    <div className="space-y-10">
      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-4xl font-bold">Developer API</h1>
        <p className="mt-4 text-slate-600">Build integrations with our verification platform using streamlined REST endpoints and comprehensive response payloads.</p>
      </section>

      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <h2 className="text-2xl font-semibold">Available Endpoints</h2>
        <div className="mt-6 space-y-4 text-slate-700">
          <p><strong>POST /api/auth/register</strong> — create a new secure user account.</p>
          <p><strong>POST /api/auth/login</strong> — authenticate and receive a JWT token.</p>
          <p><strong>POST /api/analysis/predict</strong> — submit content for credibility verification.</p>
          <p><strong>POST /api/analysis/{'{analysis_id}'}/feedback</strong> — provide feedback on a verified result.</p>
          <p><strong>GET /api/user/profile</strong> — retrieve profile statistics and usage history.</p>
          <p><strong>GET /api/pages/*</strong> — fetch structured page content, sources, and analytics.</p>
        </div>
        <div className="mt-8 rounded-3xl bg-slate-50 p-6">
          <p className="text-slate-700">Use this API for dashboards, research systems, or content moderation workflows.</p>
        </div>
      </section>
    </div>
  )
}
