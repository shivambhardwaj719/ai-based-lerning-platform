"use client";

import { motion } from "framer-motion";
import { Sidebar } from "@/components/layout/sidebar";
import {
  Search, Filter, Code2, Clock, BarChart2, CheckCircle2,
  ChevronRight, Flame, Target, Zap, SlidersHorizontal
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";
import { cn } from "@/lib/utils";
import Link from "next/link";

const difficulties = ["All", "Easy", "Medium", "Hard"];
const topics = ["All", "Arrays", "Strings", "Linked Lists", "Trees", "Graphs", "DP", "Sorting", "Binary Search", "Stack/Queue", "Hashing"];

const problems = [
  { id: 1, title: "Two Sum", difficulty: "Easy", topic: "Arrays", acceptance: "52%", solved: true, points: 10 },
  { id: 2, title: "Valid Parentheses", difficulty: "Easy", topic: "Stack/Queue", acceptance: "66%", solved: true, points: 10 },
  { id: 3, title: "Longest Substring Without Repeating Characters", difficulty: "Medium", topic: "Strings", acceptance: "34%", solved: false, points: 20 },
  { id: 4, title: "Merge Intervals", difficulty: "Medium", topic: "Arrays", acceptance: "45%", solved: false, points: 20 },
  { id: 5, title: "Binary Tree Level Order Traversal", difficulty: "Medium", topic: "Trees", acceptance: "60%", solved: true, points: 20 },
  { id: 6, title: "Maximum Subarray", difficulty: "Medium", topic: "DP", acceptance: "50%", solved: false, points: 20 },
  { id: 7, title: "Trapping Rain Water", difficulty: "Hard", topic: "Arrays", acceptance: "58%", solved: false, points: 40 },
  { id: 8, title: "LRU Cache", difficulty: "Medium", topic: "Hashing", acceptance: "38%", solved: false, points: 30 },
  { id: 9, title: "Word Break", difficulty: "Medium", topic: "DP", acceptance: "44%", solved: false, points: 20 },
  { id: 10, title: "Median of Two Sorted Arrays", difficulty: "Hard", topic: "Binary Search", acceptance: "35%", solved: false, points: 50 },
  { id: 11, title: "Climbing Stairs", difficulty: "Easy", topic: "DP", acceptance: "72%", solved: true, points: 10 },
  { id: 12, title: "Course Schedule", difficulty: "Medium", topic: "Graphs", acceptance: "46%", solved: false, points: 20 },
];

const difficultyColor = {
  Easy: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
  Medium: "text-amber-500 bg-amber-500/10 border-amber-500/20",
  Hard: "text-rose-500 bg-rose-500/10 border-rose-500/20",
};

export default function PracticePage() {
  const [search, setSearch] = useState("");
  const [activeDiff, setActiveDiff] = useState("All");
  const [activeTopic, setActiveTopic] = useState("All");

  const filtered = problems.filter((p) => {
    const matchSearch = p.title.toLowerCase().includes(search.toLowerCase());
    const matchDiff = activeDiff === "All" || p.difficulty === activeDiff;
    const matchTopic = activeTopic === "All" || p.topic === activeTopic;
    return matchSearch && matchDiff && matchTopic;
  });

  const solved = problems.filter((p) => p.solved).length;

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6 lg:p-8">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight mb-1">Coding Practice</h1>
          <p className="text-muted-foreground text-sm">Solve problems, get AI hints, improve your skills</p>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Solved", value: `${solved}/${problems.length}`, icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-500/10" },
            { label: "Easy", value: `${problems.filter(p => p.difficulty === "Easy" && p.solved).length}/${problems.filter(p => p.difficulty === "Easy").length}`, icon: Target, color: "text-emerald-400", bg: "bg-emerald-500/10" },
            { label: "Medium", value: `${problems.filter(p => p.difficulty === "Medium" && p.solved).length}/${problems.filter(p => p.difficulty === "Medium").length}`, icon: Flame, color: "text-amber-400", bg: "bg-amber-500/10" },
            { label: "Hard", value: `${problems.filter(p => p.difficulty === "Hard" && p.solved).length}/${problems.filter(p => p.difficulty === "Hard").length}`, icon: Zap, color: "text-rose-400", bg: "bg-rose-500/10" },
          ].map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className="rounded-2xl border border-border/40 bg-card/60 p-4 flex items-center gap-3"
            >
              <div className={`h-9 w-9 rounded-xl ${s.bg} flex items-center justify-center shrink-0`}>
                <s.icon className={`h-4 w-4 ${s.color}`} />
              </div>
              <div>
                <p className="text-lg font-bold">{s.value}</p>
                <p className="text-xs text-muted-foreground">{s.label}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-col gap-4 mb-6"
        >
          <div className="flex gap-3 flex-wrap">
            <div className="relative flex-1 min-w-48">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search problems..."
                className="pl-9 h-9 rounded-xl border-border/60 bg-muted/30 text-sm"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-1 rounded-xl bg-muted/40 border border-border/40 p-1">
              {difficulties.map((d) => (
                <button
                  key={d}
                  onClick={() => setActiveDiff(d)}
                  className={cn(
                    "px-3 py-1 rounded-lg text-xs font-medium transition-colors",
                    activeDiff === d ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Topic filters - scrollable */}
          <div className="flex gap-2 overflow-x-auto scrollbar-thin pb-1">
            {topics.map((t) => (
              <button
                key={t}
                onClick={() => setActiveTopic(t)}
                className={cn(
                  "px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors border",
                  activeTopic === t
                    ? "bg-primary/10 text-primary border-primary/20"
                    : "border-border/40 text-muted-foreground hover:text-foreground hover:border-border bg-transparent"
                )}
              >
                {t}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Problems table */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="rounded-2xl border border-border/40 bg-card/60 overflow-hidden"
        >
          {/* Table header */}
          <div className="grid grid-cols-[32px_1fr_auto_auto_auto] gap-4 px-5 py-3 border-b border-border/40 bg-muted/30 text-xs font-medium text-muted-foreground">
            <span>#</span>
            <span>Title</span>
            <span className="hidden sm:block">Topic</span>
            <span className="hidden md:block">Acceptance</span>
            <span>Difficulty</span>
          </div>

          {filtered.map((problem, i) => (
            <motion.div
              key={problem.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.03 }}
            >
              <Link href={`/practice/${problem.id}`}>
                <div className="grid grid-cols-[32px_1fr_auto_auto_auto] gap-4 px-5 py-3.5 border-b border-border/40 hover:bg-muted/30 transition-colors items-center group">
                  <span className="text-xs text-muted-foreground">{problem.id}</span>
                  <div className="flex items-center gap-2 min-w-0">
                    {problem.solved && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />}
                    <span className={cn(
                      "text-sm font-medium truncate group-hover:text-primary transition-colors",
                      problem.solved ? "text-muted-foreground" : "text-foreground"
                    )}>
                      {problem.title}
                    </span>
                  </div>
                  <Badge variant="outline" className="hidden sm:flex text-xs border-border/40 text-muted-foreground">
                    {problem.topic}
                  </Badge>
                  <span className="hidden md:block text-xs text-muted-foreground">{problem.acceptance}</span>
                  <Badge className={cn("text-xs border", difficultyColor[problem.difficulty as keyof typeof difficultyColor])}>
                    {problem.difficulty}
                  </Badge>
                </div>
              </Link>
            </motion.div>
          ))}

          {filtered.length === 0 && (
            <div className="py-16 text-center text-muted-foreground">
              <Code2 className="h-8 w-8 mx-auto mb-3 opacity-40" />
              <p className="text-sm">No problems match your filters</p>
            </div>
          )}
        </motion.div>
      </main>
    </div>
  );
}
