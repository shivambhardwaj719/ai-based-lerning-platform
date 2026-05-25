"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/useAppStore";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  BookOpen,
  Code2,
  Map,
  Brain,
  Trophy,
  Terminal,
  Cpu,
  FlaskConical,
  Users,
  BarChart2,
  Settings,
  ChevronLeft,
  Flame,
  Star,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

const navItems = [
  {
    section: "Overview",
    items: [
      { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
      { label: "My Roadmap", href: "/roadmap", icon: Map },
      { label: "Progress", href: "/analytics", icon: BarChart2 },
    ],
  },
  {
    section: "Learn",
    items: [
      { label: "Study Material", href: "/learn", icon: BookOpen },
      { label: "Coding Practice", href: "/practice", icon: Code2 },
      { label: "AI Mentor", href: "/mentor", icon: Brain, badge: "AI" },
    ],
  },
  {
    section: "Labs",
    items: [
      { label: "System Design", href: "/system-design", icon: Cpu },
      { label: "DevOps Labs", href: "/labs", icon: Terminal },
      { label: "AI Playground", href: "/ai-playground", icon: FlaskConical },
    ],
  },
  {
    section: "Community",
    items: [
      { label: "Contests", href: "/contests", icon: Trophy },
      { label: "Discussions", href: "/community", icon: Users },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isSidebarOpen, toggleSidebar, user } = useAppStore();

  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
            onClick={toggleSidebar}
          />
        )}
      </AnimatePresence>

      <motion.aside
        initial={false}
        animate={{ width: isSidebarOpen ? 240 : 60 }}
        transition={{ duration: 0.25, ease: "easeInOut" }}
        className={cn(
          "fixed left-0 top-0 z-50 flex h-screen flex-col border-r border-border/40 bg-sidebar overflow-hidden",
          "lg:sticky lg:top-0 lg:h-screen"
        )}
      >
        {/* Logo */}
        <div className="flex h-14 items-center justify-between px-3 border-b border-border/40">
          <AnimatePresence>
            {isSidebarOpen && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="flex items-center gap-2"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
                  <Zap className="h-3.5 w-3.5 text-primary" />
                </div>
                <span className="font-bold text-sm tracking-tight">
                  Nexus<span className="gradient-text">Learn</span>
                </span>
              </motion.div>
            )}
          </AnimatePresence>
          {!isSidebarOpen && (
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 mx-auto">
              <Zap className="h-3.5 w-3.5 text-primary" />
            </div>
          )}
          {isSidebarOpen && (
            <button
              onClick={toggleSidebar}
              className="flex h-6 w-6 items-center justify-center rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        {/* Streak banner */}
        <AnimatePresence>
          {isSidebarOpen && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="mx-3 mt-3 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 p-3"
            >
              <div className="flex items-center gap-2 mb-1.5">
                <Flame className="h-3.5 w-3.5 text-amber-500" />
                <span className="text-xs font-semibold text-amber-500">7-day streak!</span>
              </div>
              <Progress value={70} className="h-1.5" />
              <p className="text-[10px] text-muted-foreground mt-1">3 more days to unlock badge</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto scrollbar-thin py-3 px-2">
          {navItems.map((section) => (
            <div key={section.section} className="mb-4">
              <AnimatePresence>
                {isSidebarOpen && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="px-2 py-1 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60"
                  >
                    {section.section}
                  </motion.p>
                )}
              </AnimatePresence>
              {section.items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                return (
                  <Link
                    key={item.label}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 px-2 py-2 rounded-lg transition-colors mb-0.5 group",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted/60",
                      !isSidebarOpen && "justify-center"
                    )}
                    title={!isSidebarOpen ? item.label : undefined}
                  >
                    <item.icon className={cn("h-4 w-4 shrink-0", isActive && "text-primary")} />
                    <AnimatePresence>
                      {isSidebarOpen && (
                        <motion.span
                          initial={{ opacity: 0, width: 0 }}
                          animate={{ opacity: 1, width: "auto" }}
                          exit={{ opacity: 0, width: 0 }}
                          className="text-sm font-medium flex-1 whitespace-nowrap overflow-hidden"
                        >
                          {item.label}
                        </motion.span>
                      )}
                    </AnimatePresence>
                    {isSidebarOpen && (item as any).badge && (
                      <Badge className="text-[10px] px-1.5 py-0 h-4 bg-primary/10 text-primary border-primary/20">
                        {(item as any).badge}
                      </Badge>
                    )}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* User section */}
        <div className="border-t border-border/40 p-3">
          <div
            className={cn(
              "flex items-center gap-3 rounded-xl p-2 hover:bg-muted/60 transition-colors cursor-pointer",
              !isSidebarOpen && "justify-center"
            )}
          >
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 text-white text-xs font-bold">
              {user?.name?.[0] ?? "S"}
            </div>
            <AnimatePresence>
              {isSidebarOpen && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex-1 min-w-0"
                >
                  <p className="text-xs font-medium truncate">{user?.name ?? "Student"}</p>
                  <p className="text-[10px] text-muted-foreground truncate">{user?.email ?? "Sign in to track"}</p>
                </motion.div>
              )}
            </AnimatePresence>
            {isSidebarOpen && (
              <Link href="/settings">
                <Settings className="h-3.5 w-3.5 text-muted-foreground hover:text-foreground transition-colors" />
              </Link>
            )}
          </div>
        </div>
      </motion.aside>
    </>
  );
}
