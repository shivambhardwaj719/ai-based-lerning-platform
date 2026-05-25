"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useTheme } from "next-themes";
import {
  Moon,
  Sun,
  Zap,
  Menu,
  X,
  ChevronDown,
  Code2,
  BookOpen,
  LayoutDashboard,
  Trophy,
  Users,
  Brain,
  Map,
  FlaskConical,
  Terminal,
  Cpu,
  Flame,
  Bell,
  Search,
} from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

const navLinks = [
  {
    label: "Learn",
    href: "/learn",
    icon: BookOpen,
    mega: [
      { label: "Study Material", href: "/learn", icon: BookOpen, desc: "Structured topic guides" },
      { label: "Roadmaps", href: "/roadmap", icon: Map, desc: "Guided learning paths" },
      { label: "Flashcards", href: "/flashcards", icon: Brain, desc: "Quick revision" },
    ],
  },
  {
    label: "Practice",
    href: "/practice",
    icon: Code2,
    mega: [
      { label: "Coding Problems", href: "/practice", icon: Code2, desc: "500+ curated problems" },
      { label: "System Design", href: "/system-design", icon: Cpu, desc: "Architect real systems" },
      { label: "DevOps Labs", href: "/labs", icon: Terminal, desc: "Hands-on cloud labs" },
      { label: "AI Playground", href: "/ai-playground", icon: FlaskConical, desc: "Experiment with AI" },
    ],
  },
  { label: "Contests", href: "/contests", icon: Trophy },
  { label: "AI Mentor", href: "/mentor", icon: Brain },
  { label: "Community", href: "/community", icon: Users },
];

export function Navbar() {
  const { setTheme, theme, resolvedTheme } = useTheme();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const isDark = mounted && resolvedTheme === "dark";

  return (
    <header
      className={cn(
        "sticky top-0 z-50 w-full transition-all duration-300",
        scrolled
          ? "border-b border-border/60 bg-background/90 backdrop-blur-xl shadow-sm shadow-black/5"
          : "bg-transparent"
      )}
    >
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 ring-1 ring-primary/20 group-hover:bg-primary/20 transition-colors">
              <Zap className="h-4 w-4 text-primary" />
              <div className="absolute inset-0 rounded-lg bg-primary/5 animate-pulse-glow" />
            </div>
            <span className="font-bold text-lg tracking-tight">
              Nexus<span className="gradient-text">Learn</span>
            </span>
            <Badge variant="secondary" className="text-[10px] px-1.5 py-0 h-4 font-medium hidden sm:flex">
              AI
            </Badge>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <div
                key={link.label}
                className="relative"
                onMouseEnter={() => link.mega && setActiveDropdown(link.label)}
                onMouseLeave={() => setActiveDropdown(null)}
              >
                <Link
                  href={link.href}
                  className={cn(
                    "flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    pathname === link.href
                      ? "text-foreground bg-muted"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/60"
                  )}
                >
                  {link.label}
                  {link.mega && <ChevronDown className="h-3 w-3 opacity-60" />}
                </Link>

                {link.mega && (
                  <AnimatePresence>
                    {activeDropdown === link.label && (
                      <motion.div
                        initial={{ opacity: 0, y: 8, scale: 0.97 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 8, scale: 0.97 }}
                        transition={{ duration: 0.15 }}
                        className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-72 rounded-2xl border border-border/60 bg-popover/95 backdrop-blur-xl p-2 shadow-xl shadow-black/20"
                      >
                        {link.mega.map((item) => (
                          <Link
                            key={item.label}
                            href={item.href}
                            className="flex items-start gap-3 p-3 rounded-xl hover:bg-muted/60 transition-colors group"
                          >
                            <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                              <item.icon className="h-4 w-4 text-primary" />
                            </div>
                            <div>
                              <div className="text-sm font-medium text-foreground">{item.label}</div>
                              <div className="text-xs text-muted-foreground">{item.desc}</div>
                            </div>
                          </Link>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                )}
              </div>
            ))}
          </nav>

          {/* Right Actions */}
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground hidden sm:flex">
              <Search className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground hidden sm:flex relative">
              <Bell className="h-4 w-4" />
              <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full bg-primary" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
              onClick={() => mounted && setTheme(isDark ? "light" : "dark")}
            >
              {mounted ? (
                isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />
              ) : (
                <div className="h-4 w-4 rounded-full bg-muted animate-pulse" />
              )}
            </Button>
            <div className="hidden sm:flex items-center gap-2">
              <Link href="/login">
                <Button variant="ghost" size="sm" className="h-8 text-sm">
                  Log in
                </Button>
              </Link>
              <Link href="/signup">
                <Button size="sm" className="h-8 text-sm bg-primary hover:bg-primary/90 rounded-lg px-4">
                  Get Started
                </Button>
              </Link>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 md:hidden"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-border/40 bg-background/95 backdrop-blur-xl overflow-hidden"
          >
            <div className="container px-4 py-4 space-y-1">
              {navLinks.map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors",
                    pathname === link.href
                      ? "text-primary bg-primary/10"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  )}
                >
                  <link.icon className="h-4 w-4" />
                  {link.label}
                </Link>
              ))}
              <div className="pt-2 flex gap-2">
                <Link href="/login" className="flex-1">
                  <Button variant="outline" className="w-full h-9">Log in</Button>
                </Link>
                <Link href="/signup" className="flex-1">
                  <Button className="w-full h-9">Get Started</Button>
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
