import { Search, ArrowRight } from "lucide-react";
import { useState } from "react";
import heroBg from "@/assets/hero-bg.jpg";
import ResultCard from "./ResultCard";

const HeroSection = () => {
  const [query, setQuery] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<null | { verdict: "real" | "fake" | "uncertain"; confidence: number; summary: string }>(null);

  const handleCheck = () => {
    if (!query.trim()) return;
    setIsAnalyzing(true);
    setResult(null);

    // Simulate analysis
    setTimeout(() => {
      const verdicts: Array<"real" | "fake" | "uncertain"> = ["real", "fake", "uncertain"];
      const verdict = verdicts[Math.floor(Math.random() * 3)];
      setResult({
        verdict,
        confidence: Math.floor(Math.random() * 30) + 70,
        summary:
          verdict === "fake"
            ? "This article contains multiple unverified claims and originates from an unreliable source. Key facts could not be corroborated."
            : verdict === "real"
            ? "This article's claims are supported by multiple credible sources. The information aligns with verified reporting."
            : "Some claims in this article could not be fully verified. We recommend checking additional sources.",
      });
      setIsAnalyzing(false);
    }, 2000);
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center pt-16 overflow-hidden">
      <div className="absolute inset-0 z-0">
        <img src={heroBg} alt="" className="w-full h-full object-cover opacity-30" width={1920} height={1080} />
        <div className="absolute inset-0 bg-gradient-to-b from-background/60 via-background/80 to-background" />
      </div>

      <div className="container relative z-10 mx-auto px-6 py-20 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 mb-8">
          <span className="h-2 w-2 rounded-full bg-accent animate-pulse" />
          <span className="text-xs font-medium text-primary">AI-Powered Fact Checking</span>
        </div>

        <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold leading-tight mb-6 max-w-4xl mx-auto">
          Detect <span className="text-gradient">Fake News</span> Before It Spreads
        </h1>

        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-12">
          Paste any article, headline, or URL and our AI will analyze it for misinformation, bias, and factual accuracy in seconds.
        </p>

        <div id="check" className="max-w-2xl mx-auto">
          <div className="glass-card rounded-2xl p-2 flex flex-col sm:flex-row gap-2">
            <div className="flex-1 flex items-center gap-3 px-4">
              <Search className="h-5 w-5 text-muted-foreground shrink-0" />
              <input
                type="text"
                placeholder="Paste a headline, article text, or URL..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleCheck()}
                className="w-full bg-transparent text-foreground placeholder:text-muted-foreground outline-none py-3 text-sm"
              />
            </div>
            <button
              onClick={handleCheck}
              disabled={isAnalyzing || !query.trim()}
              className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-50 shrink-0"
            >
              {isAnalyzing ? (
                <>
                  <span className="h-4 w-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  Analyze <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>

          {result && <ResultCard {...result} />}
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
