import { Shield, Menu, X, LogOut, User, ChevronDown } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { user, signOut } = useAuth();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-xl border-b border-border/50">
      <div className="container mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <Shield className="h-7 w-7 text-primary" />
          <span className="text-lg font-bold text-foreground">TruthLens</span>
        </Link>

        <div className="hidden md:flex items-center gap-8">
          <a href="#how-it-works" className="text-sm text-muted-foreground hover:text-foreground transition-colors">How It Works</a>
          <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</a>
          <a href="#stats" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Stats</a>
          {user ? (
            <div className="flex items-center gap-2 relative">
              <button 
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-secondary text-secondary-foreground text-sm font-semibold hover:bg-secondary/80 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="h-4 w-4 text-primary" />
                </div>
                <span className="max-w-24 truncate">{user.username || user.name || user.email}</span>
                <ChevronDown className="h-4 w-4" />
              </button>
              {userMenuOpen && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-background border border-border rounded-lg shadow-lg py-2">
                  <button 
                    onClick={signOut}
                    className="w-full flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/auth" className="px-5 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity">
              Sign In
            </Link>
          )}
        </div>

        <button className="md:hidden text-foreground" onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" /> }
        </button>
      </div>

      {isOpen && (
        <div className="md:hidden bg-background border-b border-border px-6 py-4 flex flex-col gap-4">
          <a href="#how-it-works" className="text-sm text-muted-foreground">How It Works</a>
          <a href="#features" className="text-sm text-muted-foreground">Features</a>
          <a href="#stats" className="text-sm text-muted-foreground">Stats</a>
          {user ? (
            <div className="flex flex-col items-center gap-2 text-sm">
              <span className="font-semibold">{user.username || user.email}</span>
              <button onClick={signOut} className="px-6 py-2 rounded-lg bg-destructive text-destructive-foreground text-sm font-semibold w-full">
                Sign Out
              </button>
            </div>
          ) : (
            <Link to="/auth" className="px-5 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-semibold text-center">Sign In</Link>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
