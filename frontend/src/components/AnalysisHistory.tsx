import { useMemo, useState } from "react";
import { MessageSquare, ThumbsDown, ThumbsUp, ExternalLink, History } from "lucide-react";
import { apiRequest } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export interface AnalysisFeedback {
  id: number;
  analysis_id: number;
  user_id: number | null;
  is_correct: boolean;
  user_correction: string | null;
  comment: string | null;
  created_at: string;
}

export interface SavedAnalysis {
  id: number;
  user_id: number | null;
  text_length: number;
  source_type: string | null;
  source_url: string | null;
  text_preview: string | null;
  prediction: string;
  confidence: number | null;
  reasons: string[];
  processing_time: number;
  created_at: string;
  feedback: AnalysisFeedback[];
}

interface AnalysisHistoryProps {
  analyses: SavedAnalysis[];
  currentUserId?: number;
  loading: boolean;
  onFeedbackSaved: (analysisId: number, feedback: AnalysisFeedback) => void;
}

const correctionOptions = ["Real", "Fake", "Uncertain"];

const formatPredictionTone = (prediction: string) => {
  const normalized = prediction.toLowerCase();
  if (normalized === "real") {
    return {
      label: "Likely true",
      classes: "border-emerald-500/30 bg-emerald-500/10 text-emerald-700",
    };
  }

  if (normalized === "fake") {
    return {
      label: "Likely false",
      classes: "border-red-500/30 bg-red-500/10 text-red-700",
    };
  }

  return {
    label: prediction,
    classes: "border-amber-500/30 bg-amber-500/10 text-amber-700",
  };
};

const AnalysisHistory = ({
  analyses,
  currentUserId,
  loading,
  onFeedbackSaved,
}: AnalysisHistoryProps) => {
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [commentById, setCommentById] = useState<Record<number, string>>({});
  const [correctionById, setCorrectionById] = useState<Record<number, string>>({});
  const [submittingId, setSubmittingId] = useState<number | null>(null);
  const { toast } = useToast();

  const feedbackLookup = useMemo(() => {
    return analyses.reduce<Record<number, AnalysisFeedback | null>>((accumulator, analysis) => {
      accumulator[analysis.id] =
        analysis.feedback.find((item) => item.user_id === currentUserId) ??
        analysis.feedback[0] ??
        null;
      return accumulator;
    }, {});
  }, [analyses, currentUserId]);

  const submitFeedback = async (analysisId: number, isCorrect: boolean) => {
    setSubmittingId(analysisId);

    try {
      const response = await apiRequest<{
        feedback: AnalysisFeedback;
        message: string;
      }>(`/api/analysis/${analysisId}/feedback`, {
        method: "POST",
        body: JSON.stringify({
          analysis_id: analysisId,
          is_correct: isCorrect,
          user_correction: isCorrect ? null : correctionById[analysisId] || null,
          comment: commentById[analysisId]?.trim() || null,
        }),
      });

      onFeedbackSaved(analysisId, response.feedback);
      toast({
        title: "Feedback saved",
        description: response.message,
      });
    } catch (error: any) {
      toast({
        title: "Could not save feedback",
        description: error?.error || "Please try again.",
        variant: "destructive",
      });
    } finally {
      setSubmittingId(null);
    }
  };

  return (
    <section className="container mx-auto px-6 pb-20">
      <div id="history" className="glass-card rounded-3xl border border-border/60 p-6 md:p-8">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
              <History className="h-3.5 w-3.5" />
              Review saved analyses
            </div>
            <h2 className="mt-4 text-2xl font-bold text-foreground">Your past checks stay available for later review</h2>
            <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
              Each signed-in analysis is saved with its verdict, source details, and your feedback so you can revisit earlier decisions.
            </p>
          </div>
          <div className="rounded-2xl border border-border/60 bg-background/60 px-4 py-3 text-sm text-muted-foreground">
            {analyses.length} saved {analyses.length === 1 ? "analysis" : "analyses"}
          </div>
        </div>

        {loading ? (
          <div className="mt-8 rounded-2xl border border-dashed border-border/60 px-6 py-12 text-center text-sm text-muted-foreground">
            Loading your saved analysis history...
          </div>
        ) : analyses.length === 0 ? (
          <div className="mt-8 rounded-2xl border border-dashed border-border/60 px-6 py-12 text-center text-sm text-muted-foreground">
            Run your first analysis while signed in and it will appear here automatically.
          </div>
        ) : (
          <div className="mt-8 space-y-4">
            {analyses.map((analysis) => {
              const tone = formatPredictionTone(analysis.prediction);
              const savedFeedback = feedbackLookup[analysis.id];
              const isExpanded = expandedId === analysis.id;

              return (
                <article
                  key={analysis.id}
                  className="rounded-2xl border border-border/60 bg-background/70 p-5 shadow-sm"
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="space-y-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${tone.classes}`}>
                          {tone.label}
                        </span>
                        <span className="rounded-full border border-border/60 px-3 py-1 text-xs text-muted-foreground">
                          {Math.round(analysis.confidence ?? 0)}% confidence
                        </span>
                        <span className="rounded-full border border-border/60 px-3 py-1 text-xs text-muted-foreground">
                          {analysis.source_type || "article"}
                        </span>
                      </div>

                      <p className="text-sm leading-6 text-foreground">
                        {analysis.text_preview || "No preview available for this saved analysis."}
                      </p>

                      <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                        <span>{new Date(analysis.created_at).toLocaleString()}</span>
                        <span>{analysis.text_length} words checked</span>
                        <span>{Math.round(analysis.processing_time)} ms</span>
                        {analysis.source_url ? (
                          <a
                            href={analysis.source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-primary hover:underline"
                          >
                            Open source <ExternalLink className="h-3.5 w-3.5" />
                          </a>
                        ) : null}
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => setExpandedId(isExpanded ? null : analysis.id)}
                      className="rounded-xl border border-border/60 px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
                    >
                      {isExpanded ? "Hide details" : "Review details"}
                    </button>
                  </div>

                  {isExpanded ? (
                    <div className="mt-5 space-y-5 border-t border-border/60 pt-5">
                      <div>
                        <h3 className="text-sm font-semibold text-foreground">Why the model leaned this way</h3>
                        {analysis.reasons.length > 0 ? (
                          <div className="mt-3 flex flex-wrap gap-2">
                            {analysis.reasons.map((reason, index) => (
                              <span
                                key={`${analysis.id}-${index}`}
                                className="rounded-full border border-border/60 bg-secondary/50 px-3 py-1 text-xs text-muted-foreground"
                              >
                                {reason}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <p className="mt-2 text-sm text-muted-foreground">
                            No extra warning signals were stored for this result.
                          </p>
                        )}
                      </div>

                      <div className="rounded-2xl border border-border/60 bg-secondary/20 p-4">
                        <div className="flex items-center gap-2">
                          <MessageSquare className="h-4 w-4 text-primary" />
                          <h3 className="text-sm font-semibold text-foreground">Feedback</h3>
                        </div>

                        {savedFeedback ? (
                          <p className="mt-3 text-sm text-muted-foreground">
                            Saved feedback: {savedFeedback.is_correct ? "Marked as correct" : "Marked for correction"}
                            {savedFeedback.user_correction ? ` (${savedFeedback.user_correction})` : ""}
                            {savedFeedback.comment ? ` - ${savedFeedback.comment}` : ""}
                          </p>
                        ) : (
                          <p className="mt-3 text-sm text-muted-foreground">
                            Tell us whether this result looks right. Your feedback is stored with the analysis.
                          </p>
                        )}

                        <div className="mt-4 flex flex-wrap gap-3">
                          <button
                            type="button"
                            disabled={submittingId === analysis.id}
                            onClick={() => submitFeedback(analysis.id, true)}
                            className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                          >
                            <ThumbsUp className="h-4 w-4" />
                            This looks right
                          </button>
                          <button
                            type="button"
                            disabled={submittingId === analysis.id}
                            onClick={() => submitFeedback(analysis.id, false)}
                            className="inline-flex items-center gap-2 rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                          >
                            <ThumbsDown className="h-4 w-4" />
                            Needs correction
                          </button>
                        </div>

                        <div className="mt-4 grid gap-3 md:grid-cols-[180px,1fr]">
                          <select
                            value={correctionById[analysis.id] || ""}
                            onChange={(event) =>
                              setCorrectionById((current) => ({
                                ...current,
                                [analysis.id]: event.target.value,
                              }))
                            }
                            className="rounded-xl border border-border/60 bg-background px-3 py-2 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30"
                          >
                            <option value="">Suggested correction</option>
                            {correctionOptions.map((option) => (
                              <option key={option} value={option}>
                                {option}
                              </option>
                            ))}
                          </select>

                          <textarea
                            rows={3}
                            value={commentById[analysis.id] || ""}
                            onChange={(event) =>
                              setCommentById((current) => ({
                                ...current,
                                [analysis.id]: event.target.value,
                              }))
                            }
                            placeholder="Add any notes about why this result was right or wrong."
                            className="rounded-xl border border-border/60 bg-background px-3 py-2 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30"
                          />
                        </div>
                      </div>
                    </div>
                  ) : null}
                </article>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
};

export default AnalysisHistory;
