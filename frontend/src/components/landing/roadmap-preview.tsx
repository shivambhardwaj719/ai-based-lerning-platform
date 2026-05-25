"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { CheckCircle2, Circle, Lock, ArrowRight, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { cn } from "@/lib/utils";

const roadmapNodes = [
  { id: 1, label: "Python Basics", status: "done", time: "2 weeks" },
  { id: 2, label: "OOP Concepts", status: "done", time: "1 week" },
  { id: 3, label: "Data Structures", status: "active", time: "3 weeks", current: true },
  { id: 4, label: "Algorithms", status: "upcoming", time: "4 weeks" },
  { id: 5, label: "System Design", status: "locked", time: "6 weeks" },
  { id: 6, label: "Backend APIs", status: "locked", time: "3 weeks" },
];

export function RoadmapPreview() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="py-24 bg-background" ref={ref}>
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: copy */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-muted/40 px-4 py-1.5 mb-5">
              <Zap className="h-3.5 w-3.5 text-primary" />
              <span className="text-sm font-medium text-muted-foreground">Personalized Roadmaps</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight leading-tight mb-5">
              Your personalized<br />
              <span className="gradient-text">path to mastery</span>
            </h2>
            <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
              AI analyzes your goals, current skill level, and learning style to create a
              step-by-step roadmap. Every concept builds on the last — no confusion, no gaps.
            </p>
            <ul className="space-y-3 mb-8">
              {[
                "Beginner to expert paths for 30+ technologies",
                "AI adjusts your roadmap based on progress",
                "Visual prerequisite map — see the full picture",
                "Estimated time for every topic",
              ].map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm text-muted-foreground">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
            <Link href="/roadmap">
              <Button size="lg" className="h-11 rounded-xl group">
                Explore Roadmaps
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
          </motion.div>

          {/* Right: visual */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="relative"
          >
            <div className="gradient-border rounded-2xl p-6 bg-card/60">
              <div className="flex items-center justify-between mb-5">
                <div>
                  <h3 className="font-semibold text-sm">Python Developer Path</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">19 weeks · Beginner → Advanced</p>
                </div>
                <Badge className="bg-primary/10 text-primary border-primary/20 text-xs">In Progress</Badge>
              </div>

              {/* Progress bar */}
              <div className="mb-6">
                <div className="flex justify-between text-xs text-muted-foreground mb-1.5">
                  <span>Overall Progress</span>
                  <span className="font-medium text-foreground">38%</span>
                </div>
                <div className="h-2 rounded-full bg-muted">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={inView ? { width: "38%" } : {}}
                    transition={{ delay: 0.5, duration: 1, ease: "easeOut" }}
                    className="h-full rounded-full bg-gradient-to-r from-primary to-cyan-500"
                  />
                </div>
              </div>

              {/* Nodes */}
              <div className="space-y-3">
                {roadmapNodes.map((node, i) => (
                  <motion.div
                    key={node.id}
                    initial={{ opacity: 0, x: 10 }}
                    animate={inView ? { opacity: 1, x: 0 } : {}}
                    transition={{ delay: 0.3 + i * 0.08 }}
                    className={cn(
                      "flex items-center gap-3 p-3 rounded-xl border transition-colors",
                      node.status === "done" && "border-emerald-500/20 bg-emerald-500/5",
                      node.status === "active" && "border-primary/30 bg-primary/5",
                      node.status === "upcoming" && "border-border/40 bg-muted/30",
                      node.status === "locked" && "border-border/20 bg-muted/10 opacity-50",
                    )}
                  >
                    {node.status === "done" && <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />}
                    {node.status === "active" && (
                      <div className="h-4 w-4 rounded-full border-2 border-primary shrink-0 flex items-center justify-center">
                        <div className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
                      </div>
                    )}
                    {node.status === "upcoming" && <Circle className="h-4 w-4 text-muted-foreground shrink-0" />}
                    {node.status === "locked" && <Lock className="h-4 w-4 text-muted-foreground shrink-0" />}

                    <span className={cn(
                      "flex-1 text-sm font-medium",
                      node.status === "locked" && "text-muted-foreground",
                    )}>
                      {node.label}
                      {node.current && (
                        <Badge className="ml-2 text-[10px] bg-primary text-primary-foreground">Current</Badge>
                      )}
                    </span>
                    <span className="text-xs text-muted-foreground">{node.time}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
