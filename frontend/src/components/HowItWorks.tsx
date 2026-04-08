import { FileText, Brain, CheckCircle } from "lucide-react";

const steps = [
  {
    icon: FileText,
    title: "Paste Content",
    description: "Submit any headline, article text, or URL you want to verify.",
  },
  {
    icon: Brain,
    title: "AI Analysis",
    description: "Our model cross-references claims against trusted databases and detects linguistic patterns of misinformation.",
  },
  {
    icon: CheckCircle,
    title: "Get Results",
    description: "Receive a clear verdict with a confidence score and detailed explanation of the findings.",
  },
];

const HowItWorks = () => (
  <section id="how-it-works" className="py-24">
    <div className="container mx-auto px-6">
      <div className="text-center mb-16">
        <p className="text-sm font-semibold text-primary mb-2 tracking-wide uppercase">How It Works</p>
        <h2 className="text-3xl md:text-4xl font-bold">Three Simple Steps</h2>
      </div>

      <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        {steps.map((step, i) => (
          <div key={i} className="glass-card rounded-2xl p-8 text-center hover:border-primary/30 transition-colors group">
            <div className="inline-flex items-center justify-center h-14 w-14 rounded-xl bg-primary/10 mb-6 group-hover:bg-primary/20 transition-colors">
              <step.icon className="h-7 w-7 text-primary" />
            </div>
            <h3 className="text-lg font-bold mb-3">{step.title}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{step.description}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default HowItWorks;
