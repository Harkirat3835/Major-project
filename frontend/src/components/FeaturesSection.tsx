import { Zap, Globe, Lock, BarChart3 } from "lucide-react";

const features = [
  { icon: Zap, title: "Real-Time Analysis", desc: "Get results in seconds with our optimized AI pipeline." },
  { icon: Globe, title: "Multi-Language", desc: "Analyze content in 50+ languages with high accuracy." },
  { icon: Lock, title: "Privacy First", desc: "Your queries are never stored or shared with third parties." },
  { icon: BarChart3, title: "Detailed Reports", desc: "See source credibility scores, bias indicators, and claim breakdowns." },
];

const FeaturesSection = () => (
  <section id="features" className="py-24 bg-secondary/30">
    <div className="container mx-auto px-6">
      <div className="text-center mb-16">
        <p className="text-sm font-semibold text-primary mb-2 tracking-wide uppercase">Features</p>
        <h2 className="text-3xl md:text-4xl font-bold">Why Choose TruthLens</h2>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
        {features.map((f, i) => (
          <div key={i} className="glass-card rounded-2xl p-6 hover:border-primary/30 transition-colors">
            <f.icon className="h-8 w-8 text-primary mb-4" />
            <h3 className="font-bold mb-2">{f.title}</h3>
            <p className="text-sm text-muted-foreground">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default FeaturesSection;
