"use client";

import { motion } from "framer-motion";
import { Sidebar } from "@/components/layout/sidebar";
import {
  Map, Search, CheckCircle2, Circle, Lock, ChevronRight,
  Clock, Star, ArrowRight, Flame, Code2, Server, Brain,
  Terminal, Cpu, BookOpen, Database
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useState } from "react";
import { cn } from "@/lib/utils";

const roadmaps = [
  {
    id: "python",
    title: "Python Developer",
    icon: "🐍",
    level: "Beginner → Advanced",
    weeks: 19,
    topics: 42,
    progress: 38,
    enrolled: true,
    popular: true,
    color: "from-blue-500/20 to-cyan-500/10",
    border: "border-blue-500/30",
  },
  {
    id: "fullstack",
    title: "Full Stack Web Dev",
    icon: "🌐",
    level: "Beginner → Advanced",
    weeks: 28,
    topics: 65,
    progress: 0,
    enrolled: false,
    popular: true,
    color: "from-violet-500/20 to-purple-500/10",
    border: "border-violet-500/30",
  },
  {
    id: "devops",
    title: "DevOps & Cloud",
    icon: "☁️",
    level: "Intermediate → Advanced",
    weeks: 20,
    topics: 48,
    progress: 0,
    enrolled: false,
    color: "from-amber-500/20 to-orange-500/10",
    border: "border-amber-500/30",
  },
  {
    id: "aiml",
    title: "AI / Machine Learning",
    icon: "🤖",
    level: "Beginner → Expert",
    weeks: 32,
    topics: 70,
    progress: 0,
    enrolled: false,
    popular: true,
    color: "from-emerald-500/20 to-teal-500/10",
    border: "border-emerald-500/30",
  },
  {
    id: "systemdesign",
    title: "System Design",
    icon: "🏗️",
    level: "Intermediate → Expert",
    weeks: 12,
    topics: 30,
    progress: 0,
    enrolled: false,
    color: "from-rose-500/20 to-pink-500/10",
    border: "border-rose-500/30",
  },
  {
    id: "dsa",
    title: "Data Structures & Algorithms",
    icon: "📊",
    level: "Beginner → Advanced",
    weeks: 16,
    topics: 55,
    progress: 0,
    enrolled: false,
    color: "from-cyan-500/20 to-sky-500/10",
    border: "border-cyan-500/30",
  },
];

const pythonTopics = [
  { label: "Python Basics", subtopics: 8, done: true, time: "2 weeks" },
  { label: "Object-Oriented Programming", subtopics: 6, done: true, time: "1 week" },
  { label: "Data Structures", subtopics: 10, active: true, time: "3 weeks", progress: 40 },
  { label: "Algorithms", subtopics: 12, time: "4 weeks" },
  { label: "File I/O & Modules", subtopics: 5, time: "1 week", locked: true },
  { label: "APIs & Web Requests", subtopics: 6, time: "1.5 weeks", locked: true },
  { label: "Databases with Python", subtopics: 7, time: "2 weeks", locked: true },
  { label: "Testing & Clean Code", subtopics: 6, time: "1.5 weeks", locked: true },
];

export default function RoadmapPage() {
  const [search, setSearch] = useState("");
  const [activeRoadmap, setActiveRoadmap] = useState("python");

  const filtered = roadmaps.filter((r) =>
    r.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6 lg:p-8">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight mb-1">Learning Roadmaps</h1>
          <p className="text-muted-foreground text-sm">
            AI-curated, structured learning paths from beginner to expert
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-[280px_1fr] gap-6">
          {/* Roadmap list */}
          <div className="space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search roadmaps..."
                className="pl-9 h-9 rounded-xl border-border/60 bg-muted/30 text-sm"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            {filtered.map((roadmap, i) => (
              <motion.button
                key={roadmap.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => setActiveRoadmap(roadmap.id)}
                className={cn(
                  "w-full text-left rounded-2xl border p-4 transition-all",
                  activeRoadmap === roadmap.id
                    ? `bg-gradient-to-br ${roadmap.color} ${roadmap.border} shadow-sm`
                    : "border-border/40 bg-card/60 hover:border-border"
                )}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{roadmap.icon}</span>
                    <span className="font-semibold text-sm">{roadmap.title}</span>
                  </div>
                  {roadmap.popular && (
                    <Badge className="text-[10px] bg-amber-500/10 text-amber-500 border-amber-500/20">Popular</Badge>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground mb-2">
                  <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{roadmap.weeks}w</span>
                  <span>{roadmap.topics} topics</span>
                </div>
                {roadmap.enrolled && roadmap.progress > 0 && (
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="font-medium">{roadmap.progress}%</span>
                    </div>
                    <Progress value={roadmap.progress} className="h-1.5" />
                  </div>
                )}
                {!roadmap.enrolled && (
                  <Badge variant="outline" className="text-[10px] border-border/40">Not enrolled</Badge>
                )}
              </motion.button>
            ))}
          </div>

          {/* Active roadmap detail */}
          <motion.div
            key={activeRoadmap}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            {/* Header */}
            <div className="rounded-2xl border border-border/40 bg-card/60 p-6">
              <div className="flex items-start justify-between flex-wrap gap-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-3xl">🐍</span>
                    <div>
                      <h2 className="text-xl font-bold">Python Developer</h2>
                      <p className="text-sm text-muted-foreground">Beginner → Advanced · 19 weeks</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground max-w-lg">
                    Master Python from fundamentals to advanced topics including OOP, data structures,
                    algorithms, APIs, databases, and testing. Build real projects at every step.
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-extrabold gradient-text">38%</div>
                  <div className="text-xs text-muted-foreground">Complete</div>
                  <Button size="sm" className="mt-3 h-8 rounded-lg">
                    Continue Learning
                    <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>

              {/* Progress */}
              <div className="mt-5">
                <Progress value={38} className="h-2.5" />
                <div className="flex justify-between text-xs text-muted-foreground mt-1.5">
                  <span>16 / 42 topics completed</span>
                  <span>~11 weeks remaining</span>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-4 gap-3 mt-5">
                {[
                  { label: "Topics", value: "42" },
                  { label: "Projects", value: "8" },
                  { label: "Quizzes", value: "20" },
                  { label: "XP Available", value: "4,200" },
                ].map((s) => (
                  <div key={s.label} className="rounded-xl bg-muted/40 border border-border/40 p-3 text-center">
                    <p className="font-bold">{s.value}</p>
                    <p className="text-xs text-muted-foreground">{s.label}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Topics list */}
            <div className="space-y-2">
              <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider px-1">Topics</h3>
              {pythonTopics.map((topic, i) => (
                <motion.div
                  key={topic.label}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className={cn(
                    "rounded-2xl border p-4 transition-colors",
                    topic.done && "border-emerald-500/20 bg-emerald-500/5",
                    topic.active && "border-primary/30 bg-primary/5",
                    !topic.done && !topic.active && !topic.locked && "border-border/40 bg-card/60 hover:border-border",
                    topic.locked && "border-border/20 bg-muted/10 opacity-50",
                  )}
                >
                  <div className="flex items-center gap-3">
                    {topic.done && <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />}
                    {topic.active && (
                      <div className="h-5 w-5 rounded-full border-2 border-primary flex items-center justify-center shrink-0">
                        <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                      </div>
                    )}
                    {!topic.done && !topic.active && !topic.locked && <Circle className="h-5 w-5 text-muted-foreground shrink-0" />}
                    {topic.locked && <Lock className="h-5 w-5 text-muted-foreground shrink-0" />}

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-sm">{topic.label}</span>
                        {topic.active && <Badge className="text-[10px] bg-primary text-primary-foreground">Current</Badge>}
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">{topic.subtopics} subtopics · {topic.time}</p>
                      {topic.active && (topic as any).progress !== undefined && (
                        <div className="mt-2">
                          <Progress value={(topic as any).progress} className="h-1.5 w-32" />
                        </div>
                      )}
                    </div>

                    {!topic.locked && (
                      <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0">
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
