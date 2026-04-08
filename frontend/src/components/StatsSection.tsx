const stats = [
  { value: "2.5M+", label: "Articles Analyzed" },
  { value: "94%", label: "Detection Accuracy" },
  { value: "150+", label: "Countries Served" },
  { value: "<3s", label: "Avg Response Time" },
];

const StatsSection = () => (
  <section id="stats" className="py-24">
    <div className="container mx-auto px-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 max-w-4xl mx-auto">
        {stats.map((s, i) => (
          <div key={i} className="text-center">
            <p className="text-4xl md:text-5xl font-extrabold text-gradient mb-2">{s.value}</p>
            <p className="text-sm text-muted-foreground">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default StatsSection;
