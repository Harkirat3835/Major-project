import { useState } from "react";
import { Link } from "react-router-dom";
import { Shield, Mail, ArrowRight } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    setLoading(true);

    try {
      toast({
        title: "Password reset not supported",
        description: "This backend does not currently expose password reset email functionality. Contact support for account recovery.",
      });
      setSent(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <Link to="/" className="flex items-center justify-center gap-2 mb-10">
          <Shield className="h-8 w-8 text-primary" />
          <span className="text-2xl font-bold text-foreground">TruthLens</span>
        </Link>

        <div className="glass-card rounded-2xl p-8 text-center">
          {sent ? (
            <>
              <h1 className="text-2xl font-bold mb-2">Check your email</h1>
              <p className="text-sm text-muted-foreground mb-6">We sent a password reset link to <strong className="text-foreground">{email}</strong></p>
              <Link to="/auth" className="text-sm text-primary hover:underline">Back to sign in</Link>
            </>
          ) : (
            <>
              <h1 className="text-2xl font-bold mb-2">Reset password</h1>
              <p className="text-sm text-muted-foreground mb-8">Enter your email and we'll send you a reset link.</p>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input type="email" placeholder="Email address" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full bg-secondary/50 border border-border rounded-xl pl-10 pr-4 py-3 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-primary/50 transition-all" />
                </div>
                <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-50">
                  {loading ? <span className="h-4 w-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" /> : <>Send Reset Link <ArrowRight className="h-4 w-4" /></>}
                </button>
              </form>
              <Link to="/auth" className="text-sm text-muted-foreground hover:text-foreground mt-4 inline-block">Back to sign in</Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
