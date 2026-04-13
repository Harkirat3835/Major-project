import { Search, ArrowRight, Link2, FileText } from "lucide-react";
import { useEffect, useState } from "react";
import heroBg from "@/assets/hero-bg.jpg";
import ResultCard from "./ResultCard";
import AnalysisHistory, { type AnalysisFeedback, type SavedAnalysis } from "./AnalysisHistory";
import { apiRequest } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";

interface AnalysisResponse {
  analysis_id: number;
  prediction: string;
  confidence?: number | null;
  reasons?: string[];
  source_type?: string | null;
  source_url?: string | null;
  text_preview?: string | null;
}

interface HeroSectionProps {
  onHistoryCountChange?: (count: number) => void;
}

const mapPredictionToVerdict = (
  prediction: string,
): "real" | "fake" | "uncertain" => {
  const normalized = prediction.toLowerCase();
  if (normalized === "real") {
    return "real";
  }
  if (normalized === "fake") {
    return "fake";
  }
  return "uncertain";
};

const buildSummary = (response: AnalysisResponse) => {
  if (response.reasons && response.reasons.length > 0) {
    return response.reasons.join(" ");
  }

  if (response.prediction === "Real") {
    return "The article showed stronger credibility signals and fewer fake-news indicators in the text pattern analysis.";
  }

  if (response.prediction === "Fake") {
    return "The article showed multiple warning signs associated with misleading or unreliable reporting.";
  }

  return "The content needs a closer manual review because the available signals are mixed.";
};

const HeroSection = ({ onHistoryCountChange }: HeroSectionProps) => {
  const [articleText, setArticleText] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [history, setHistory] = useState<SavedAnalysis[]>([]);
  const [result, setResult] = useState<null | {
    verdict: "real" | "fake" | "uncertain";
    confidence: number;
    summary: string;
    reasons: string[];
    sourceLabel: string;
    savedMessage: string;
  }>(null);
  const { user } = useAuth();
  const { toast } = useToast();

  const loadHistory = async () => {
    if (!user) {
      setHistory([]);
      onHistoryCountChange?.(0);
      return;
    }

    setHistoryLoading(true);
    try {
      const response = await apiRequest<{ history: SavedAnalysis[] }>("/api/user/history", {
        method: "GET",
      });
      const nextHistory = response.history ?? [];
      setHistory(nextHistory);
      onHistoryCountChange?.(nextHistory.length);
    } catch (error: any) {
      toast({
        title: "Could not load history",
        description: error?.error || "Signed-in history is temporarily unavailable.",
        variant: "destructive",
      });
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [user]);

  const handleCheck = async () => {
    const trimmedText = articleText.trim();
    const trimmedUrl = sourceUrl.trim();

    if (!trimmedText && !trimmedUrl) {
      return;
    }

    setIsAnalyzing(true);
    setResult(null);

    try {
      const response = await apiRequest<AnalysisResponse>("/api/predict", {
        method: "POST",
        body: JSON.stringify({
          text: trimmedText || undefined,
          url: trimmedUrl || undefined,
        }),
      });

      setResult({
        verdict: mapPredictionToVerdict(response.prediction),
        confidence: Math.round(response.confidence ?? 0),
        summary: buildSummary(response),
        reasons: response.reasons ?? [],
        sourceLabel: response.source_type === "url" ? "URL analysis" : "Article analysis",
        savedMessage: user
          ? "This result was saved to your account history and can be reviewed below."
          : "Sign in if you want future analyses saved for later review.",
      });

      if (user) {
        await loadHistory();
      }
    } catch (error: any) {
      toast({
        title: "Analysis failed",
        description: error?.error || "Please add article text or a reachable URL and try again.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFeedbackSaved = (analysisId: number, feedback: AnalysisFeedback) => {
    setHistory((current) =>
      current.map((analysis) => {
        if (analysis.id !== analysisId) {
          return analysis;
        }

        const remaining = analysis.feedback.filter(
          (item) => item.user_id !== feedback.user_id || item.analysis_id !== feedback.analysis_id,
        );

        return {
          ...analysis,
          feedback: [...remaining, feedback],
        };
      }),
    );
  };

  return (
    <>
      <section className="relative flex min-h-screen items-center justify-center overflow-hidden pt-16">
        <div className="absolute inset-0 z-0">
          <img src={heroBg} alt="" className="h-full w-full object-cover opacity-30" width={1920} height={1080} />
          <div className="absolute inset-0 bg-gradient-to-b from-background/60 via-background/80 to-background" />
        </div>

        <div className="container relative z-10 mx-auto px-6 py-20">
          <div className="mx-auto max-w-4xl text-center">
            <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5">
              <span className="h-2 w-2 animate-pulse rounded-full bg-accent" />
              <span className="text-xs font-medium text-primary">AI-Powered Fact Checking</span>
            </div>

            <h1 className="mx-auto mb-6 max-w-4xl text-4xl font-extrabold leading-tight md:text-6xl lg:text-7xl">
              Review <span className="text-gradient">News Claims</span> With a Saved Audit Trail
            </h1>

            <p className="mx-auto mb-12 max-w-2xl text-lg text-muted-foreground md:text-xl">
              Paste article text or a link, get a credibility verdict in seconds, and keep every signed-in analysis available for later review and feedback.
            </p>
          </div>

          <div id="check" className="mx-auto max-w-4xl">
            <div className="glass-card rounded-3xl border border-border/60 p-4 md:p-6">
              <div className="grid gap-4 md:grid-cols-2">
                <label className="rounded-2xl border border-border/60 bg-background/60 p-4 text-left">
                  <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
                    <FileText className="h-4 w-4 text-primary" />
                    Article text
                  </div>
                  <textarea
                    rows={9}
                    placeholder="Paste the article body, headline, or claim you want checked."
                    value={articleText}
                    onChange={(event) => setArticleText(event.target.value)}
                    className="w-full resize-none bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
                  />
                </label>

                <label className="rounded-2xl border border-border/60 bg-background/60 p-4 text-left">
                  <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
                    <Link2 className="h-4 w-4 text-primary" />
                    Source URL
                  </div>
                  <div className="flex items-start gap-3">
                    <Search className="mt-3 h-5 w-5 shrink-0 text-muted-foreground" />
                    <textarea
                      rows={9}
                      placeholder="Paste the article URL here. You can use this field alone or combine it with article text."
                      value={sourceUrl}
                      onChange={(event) => setSourceUrl(event.target.value)}
                      className="w-full resize-none bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
                    />
                  </div>
                </label>
              </div>

              <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <p className="text-sm text-muted-foreground">
                  {user
                    ? "Signed-in analyses are saved automatically and can be reviewed below."
                    : "You can analyze as a guest, but sign in if you want to save results and feedback."}
                </p>
                <button
                  onClick={handleCheck}
                  disabled={isAnalyzing || (!articleText.trim() && !sourceUrl.trim())}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
                >
                  {isAnalyzing ? (
                    <>
                      <span className="h-4 w-4 rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Analyze now <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>
              </div>

              {result ? <ResultCard {...result} /> : null}
            </div>
          </div>
        </div>
      </section>

      {user ? (
        <AnalysisHistory
          analyses={history}
          currentUserId={user.id}
          loading={historyLoading}
          onFeedbackSaved={handleFeedbackSaved}
        />
      ) : null}
    </>
  );
};

export default HeroSection;
