import Link from "next/link";
import { Zap, Globe, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const footerLinks = {
  Learn: [
    { label: "Study Material", href: "/learn" },
    { label: "Roadmaps", href: "/roadmap" },
    { label: "Flashcards", href: "/flashcards" },
    { label: "Cheat Sheets", href: "/cheatsheets" },
  ],
  Practice: [
    { label: "Coding Problems", href: "/practice" },
    { label: "System Design", href: "/system-design" },
    { label: "DevOps Labs", href: "/labs" },
    { label: "AI Playground", href: "/ai-playground" },
  ],
  Platform: [
    { label: "AI Mentor", href: "/mentor" },
    { label: "Contests", href: "/contests" },
    { label: "Community", href: "/community" },
    { label: "Dashboard", href: "/dashboard" },
  ],
  Company: [
    { label: "About", href: "/about" },
    { label: "Blog", href: "/blog" },
    { label: "Careers", href: "/careers" },
    { label: "Privacy", href: "/privacy" },
  ],
};

const socials = [
  { icon: Globe, href: "#", label: "GitHub", text: "GH" },
  { icon: Globe, href: "#", label: "Twitter", text: "TW" },
  { icon: Globe, href: "#", label: "LinkedIn", text: "LI" },
  { icon: Globe, href: "#", label: "YouTube", text: "YT" },
];

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-background">
      <div className="container mx-auto px-4 max-w-7xl py-16">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8">
          {/* Brand */}
          <div className="col-span-2">
            <Link href="/" className="flex items-center gap-2.5 mb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 ring-1 ring-primary/20">
                <Zap className="h-4 w-4 text-primary" />
              </div>
              <span className="font-bold text-lg tracking-tight">
                Nexus<span className="gradient-text">Learn</span>
              </span>
              <Badge variant="secondary" className="text-[10px] px-1.5 py-0 h-4 font-medium">AI</Badge>
            </Link>
            <p className="text-sm text-muted-foreground leading-relaxed max-w-xs mb-6">
              The next-generation AI-native technical education platform. From beginner to professional.
            </p>
            <div className="flex items-center gap-3">
              {socials.map((s) => (
                <a
                  key={s.label}
                  href={s.href}
                  aria-label={s.label}
                  className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground transition-colors"
                >
                  <span className="text-[10px] font-bold">{s.text}</span>
                </a>
              ))}
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([section, links]) => (
            <div key={section}>
              <h4 className="font-semibold text-sm mb-3">{section}</h4>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 pt-8 border-t border-border/40 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} NexusLearn AI. All rights reserved.
          </p>
          <p className="text-xs text-muted-foreground">
            Built for the next generation of engineers.
          </p>
        </div>
      </div>
    </footer>
  );
}
