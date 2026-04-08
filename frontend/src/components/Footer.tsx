import { Shield } from "lucide-react";

const Footer = () => (
  <footer className="py-12 border-t border-border">
    <div className="container mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-2">
        <Shield className="h-5 w-5 text-primary" />
        <span className="font-bold text-foreground">TruthLens</span>
      </div>
      <p className="text-sm text-muted-foreground">© 2026 TruthLens. Fighting misinformation with AI.</p>
    </div>
  </footer>
);

export default Footer;
