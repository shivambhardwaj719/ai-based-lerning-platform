"use client";

import { motion } from "framer-motion";
import { Sidebar } from "@/components/layout/sidebar";
import { Search, BookOpen, Code2, ChevronRight, Clock, Brain, Star, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useState } from "react";
import { cn } from "@/lib/utils";
import Link from "next/link";

const categories = ["All", "Python", "JavaScript", "React", "DevOps", "AI/ML", "System Design", "Algorithms"];

const topics = [
  {
    id: "python-oop",
    category: "Python",
    title: "Object-Oriented Programming",
    description: "Classes, objects, inheritance, polymorphism, and encapsulation with real-world examples.",
    icon: "🐍",
    level: "Beginner",
    readTime: "35 min",
    progress: 100,
    subtopics: ["Classes & Objects", "Inheritance", "Polymorphism", "Magic Methods"],
    color: "border-blue-500/30 bg-blue-500/5",
  },
  {
    id: "js-closures",
    category: "JavaScript",
    title: "Closures & Scope",
    description: "Master how JavaScript closures work, practical patterns, and common interview questions.",
    icon: "🌐",
    level: "Intermediate",
    readTime: "25 min",
    progress: 60,
    subtopics: ["Lexical Scope", "Closure Patterns", "Module Pattern", "IIFE"],
    color: "border-yellow-500/30 bg-yellow-500/5",
  },
  {
    id: "react-hooks",
    category: "React",
    title: "React Hooks Deep Dive",
    description: "useState, useEffect, useContext, useRef, useMemo, useCallback with real examples.",
    icon: "⚛️",
    level: "Intermediate",
    readTime: "45 min",
    progress: 30,
    subtopics: ["useState", "useEffect", "Custom Hooks", "Performance"],
    color: "border-cyan-500/30 bg-cyan-500/5",
  },
  {
    id: "docker-basics",
    category: "DevOps",
    title: "Docker & Containerization",
    description: "Understand containers, images, Dockerfile, Docker Compose, and container networking.",
    icon: "🐳",
    level: "Beginner",
    readTime: "40 min",
    progress: 0,
    subtopics: ["What is Docker", "Dockerfile", "Docker Compose", "Networking"],
    color: "border-blue-500/30 bg-blue-500/5",
  },
  {
    id: "transformers",
    category: "AI/ML",
    title: "Transformer Architecture",
    description: "Self-attention, multi-head attention, positional encoding, and how GPT/BERT work.",
    icon: "🤖",
    level: "Advanced",
    readTime: "60 min",
    progress: 0,
    subtopics: ["Self-Attention", "Multi-Head Attention", "BERT vs GPT", "Fine-tuning"],
    color: "border-emerald-500/30 bg-emerald-500/5",
  },
  {
    id: "binary-search",
    category: "Algorithms",
    title: "Binary Search Mastery",
    description: "Binary search on arrays, search space, templates, and 15 common problem patterns.",
    icon: "🔍",
    level: "Beginner",
    readTime: "30 min",
    progress: 0,
    subtopics: ["Basic Binary Search", "Search Space", "Find Peak", "Rotated Array"],
    color: "border-violet-500/30 bg-violet-500/5",
  },
];

const levelColor = {
  Beginner: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
  Intermediate: "text-amber-500 bg-amber-500/10 border-amber-500/20",
  Advanced: "text-rose-500 bg-rose-500/10 border-rose-500/20",
};

export default function LearnPage() {
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  const filtered = topics.filter((t) => {
    const matchSearch = t.title.toLowerCase().includes(search.toLowerCase()) ||
      t.description.toLowerCase().includes(search.toLowerCase());
    const matchCat = activeCategory === "All" || t.category === activeCategory;
    return matchSearch && matchCat;
  });

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6 lg:p-8">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight mb-1">Study Material</h1>
          <p className="text-muted-foreground text-sm">
            AI-enhanced learning with interactive examples, quizzes, and code playgrounds
          </p>
        </motion.div>

        {/* Search & filters */}
        <div className="flex flex-col gap-4 mb-8">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search topics, concepts..."
              className="pl-9 h-10 rounded-xl border-border/60 bg-muted/30"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex gap-2 overflow-x-auto scrollbar-thin pb-1">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={cn(
                  "px-3.5 py-1.5 rounded-xl text-sm font-medium whitespace-nowrap transition-colors border",
                  activeCategory === cat
                    ? "bg-primary/10 text-primary border-primary/20"
                    : "border-border/40 text-muted-foreground hover:text-foreground bg-transparent"
                )}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Topic cards */}
        <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-5">
          {filtered.map((topic, i) => (
            <motion.div
              key={topic.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
            >
              <Link href={`/learn/${topic.id}`}>
                <div className={cn("rounded-2xl border p-5 card-hover cursor-pointer h-full flex flex-col", topic.color)}>
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-3xl">{topic.icon}</span>
                    <Badge className={cn("text-xs border", levelColor[topic.level as keyof typeof levelColor])}>
                      {topic.level}
                    </Badge>
                  </div>

                  <h3 className="font-semibold mb-2">{topic.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed mb-4 flex-1">{topic.description}</p>

                  {/* Subtopics */}
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {topic.subtopics.slice(0, 3).map((sub) => (
                      <span key={sub} className="text-xs bg-muted/60 border border-border/40 rounded-lg px-2 py-0.5 text-muted-foreground">
                        {sub}
                      </span>
                    ))}
                    {topic.subtopics.length > 3 && (
                      <span className="text-xs text-muted-foreground">+{topic.subtopics.length - 3} more</span>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />{topic.readTime}
                      </span>
                      {topic.progress > 0 && (
                        <span className="flex items-center gap-1 text-primary">
                          {topic.progress}% done
                        </span>
                      )}
                    </div>
                    {topic.progress > 0 ? (
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 rounded-full bg-muted">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-primary to-cyan-500"
                            style={{ width: `${topic.progress}%` }}
                          />
                        </div>
                      </div>
                    ) : (
                      <span className="text-xs text-primary font-medium">Start →</span>
                    )}
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
}
