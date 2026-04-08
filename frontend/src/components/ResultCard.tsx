import { ShieldCheck, ShieldAlert, AlertTriangle } from "lucide-react";

interface ResultCardProps {
  verdict: "real" | "fake" | "uncertain";
  confidence: number;
  summary: string;
}

const config = {
  real: {
    icon: ShieldCheck,
    label: "Likely Authentic",
    color: "text-accent",
    border: "border-accent/30",
    bg: "bg-accent/10",
  },
  fake: {
    icon: ShieldAlert,
    label: "Likely Fake",
    color: "text-destructive",
    border: "border-destructive/30",
    bg: "bg-destructive/10",
  },
  uncertain: {
    icon: AlertTriangle,
    label: "Uncertain",
    color: "text-warning",
    border: "border-warning/30",
    bg: "bg-warning/10",
  },
};

const ResultCard = ({ verdict, confidence, summary }: ResultCardProps) => {
  const c = config[verdict];
  const Icon = c.icon;

  return (
    <div className={`mt-6 glass-card rounded-2xl p-6 text-left border ${c.border} animate-in fade-in slide-in-from-bottom-4 duration-500`}>
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-2 rounded-lg ${c.bg}`}>
          <Icon className={`h-6 w-6 ${c.color}`} />
        </div>
        <div>
          <p className={`font-bold text-lg ${c.color}`}>{c.label}</p>
          <p className="text-xs text-muted-foreground">{confidence}% confidence</p>
        </div>
      </div>
      <p className="text-sm text-muted-foreground leading-relaxed">{summary}</p>
    </div>
  );
};

export default ResultCard;
