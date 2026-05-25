"use client";

import { motion } from "framer-motion";
import { Sidebar } from "@/components/layout/sidebar";
import { useAppStore } from "@/stores/useAppStore";
import {
  Flame, Trophy, Target, BookOpen, Code2, Brain,
  TrendingUp, Clock, CheckCircle2, ArrowRight, Zap,
  Calendar, BarChart2, Star
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import Link from "next/link";

const recentActivity = [
  { label: "Solved: Two Sum", meta: "Python · Easy", time: "2h ago", icon: "✅", points: "+10" },
  { label: "Completed: OOP in Python", meta: "Study Material", time: "Yesterday", icon: "📖", points: "+25" },
  { label: "Contest: Weekly #42", meta: "Rank: #127 / 1840", time: "2 days ago", icon: "🏆", points: "+80" },
  { label: "Lab: Docker Basics", meta: "DevOps Lab", time: "3 days ago", icon: "🐳", points: "+30" },
];

const todayGoals = [
  { label: "Solve 2 coding problems", done: true },
  { label: "Read: Recursion chapter", done: true },
  { label: "Practice: Binary Search", done: false },
  { label: "AI Mentor session (15 min)", done: false },
];

const weeklyProgress = [
  { day: "Mon", problems: 3, study: 60 },
  { day: "Tue", problems: 2, study: 45 },
  { day: "Wed", problems: 5, study: 90 },
  { day: "Thu", problems: 1, study: 30 },
  { day: "Fri", problems: 4, study: 75 },
  { day: "Sat", problems: 2, study: 50 },
  { day: "Sun", problems: 0, study: 0 },
];

export default function DashboardPage() {
  const { isSidebarOpen } = useAppStore();

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6 lg:p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                Good morning, <span className="gradient-text">Shivam</span> 👋
              </h1>
              <p className="text-muted-foreground text-sm mt-0.5">
                You&apos;re on a 7-day streak. Keep it up!
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 rounded-xl border border-amber-500/20 bg-amber-500/10 px-3 py-1.5">
                <Flame className="h-4 w-4 text-amber-500" />
                <span className="text-sm font-semibold text-amber-500">7 day streak</span>
              </div>
              <Link href="/mentor">
                <Button size="sm" className="h-8 rounded-lg">
                  <Brain className="h-3.5 w-3.5 mr-1.5" />
                  Ask AI
                </Button>
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Stats cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Problems Solved", value: "142", icon: Code2, color: "text-violet-400", bg: "bg-violet-500/10", change: "+12 this week" },
            { label: "Study Hours", value: "48h", icon: Clock, color: "text-cyan-400", bg: "bg-cyan-500/10", change: "+5h this week" },
            { label: "XP Points", value: "2,840", icon: Star, color: "text-amber-400", bg: "bg-amber-500/10", change: "+180 today" },
            { label: "Global Rank", value: "#1,284", icon: Trophy, color: "text-emerald-400", bg: "bg-emerald-500/10", change: "↑ 46 positions" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className="rounded-2xl border border-border/40 bg-card/60 p-4"
            >
              <div className={`flex h-9 w-9 items-center justify-center rounded-xl ${stat.bg} mb-3`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
              <p className="text-2xl font-bold">{stat.value}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{stat.label}</p>
              <p className="text-xs text-emerald-500 mt-1">{stat.change}</p>
            </motion.div>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Roadmap progress */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2 rounded-2xl border border-border/40 bg-card/60 p-6"
          >
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="font-semibold">Active Roadmap</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Python Developer · Week 8 of 19</p>
              </div>
              <Link href="/roadmap">
                <Button variant="ghost" size="sm" className="h-7 text-xs">
                  View all <ArrowRight className="h-3 w-3 ml-1" />
                </Button>
              </Link>
            </div>

            {/* Overall progress */}
            <div className="mb-5">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-muted-foreground">Overall Progress</span>
                <span className="font-semibold">38%</span>
              </div>
              <Progress value={38} className="h-2.5 rounded-full" />
            </div>

            {/* Current topics */}
            <div className="space-y-3">
              {[
                { label: "Data Structures — Arrays & Lists", progress: 80, status: "active" },
                { label: "Data Structures — Stacks & Queues", progress: 30, status: "active" },
                { label: "Algorithms — Sorting", progress: 0, status: "upcoming" },
              ].map((topic) => (
                <div key={topic.label} className="flex items-center gap-3">
                  <div className={`h-2 w-2 rounded-full shrink-0 ${topic.status === "active" ? "bg-primary" : "bg-muted-foreground/40"}`} />
                  <span className="text-sm flex-1 truncate">{topic.label}</span>
                  <div className="w-24 h-1.5 rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-primary to-cyan-500 transition-all"
                      style={{ width: `${topic.progress}%` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground w-8 text-right">{topic.progress}%</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Today's goals */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="rounded-2xl border border-border/40 bg-card/60 p-6"
          >
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-primary" />
                <h2 className="font-semibold">Today&apos;s Goals</h2>
              </div>
              <Badge variant="secondary" className="text-xs">2/4 done</Badge>
            </div>
            <div className="space-y-3">
              {todayGoals.map((goal) => (
                <div key={goal.label} className="flex items-start gap-3">
                  <div className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition-colors ${goal.done ? "bg-emerald-500 border-emerald-500" : "border-border"}`}>
                    {goal.done && <CheckCircle2 className="h-3 w-3 text-white" />}
                  </div>
                  <span className={`text-sm leading-5 ${goal.done ? "text-muted-foreground line-through" : "text-foreground"}`}>
                    {goal.label}
                  </span>
                </div>
              ))}
            </div>
            <div className="mt-5 pt-4 border-t border-border/40">
              <div className="flex justify-between text-xs text-muted-foreground mb-1.5">
                <span>Daily XP</span>
                <span>180 / 250</span>
              </div>
              <Progress value={72} className="h-2" />
            </div>
          </motion.div>

          {/* Weekly activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            className="rounded-2xl border border-border/40 bg-card/60 p-6"
          >
            <div className="flex items-center gap-2 mb-5">
              <BarChart2 className="h-4 w-4 text-primary" />
              <h2 className="font-semibold">Weekly Activity</h2>
            </div>
            <div className="flex items-end justify-between gap-2 h-24">
              {weeklyProgress.map((d) => {
                const maxProblems = 5;
                const height = d.problems > 0 ? Math.max((d.problems / maxProblems) * 100, 10) : 4;
                return (
                  <div key={d.day} className="flex flex-col items-center gap-1.5 flex-1">
                    <div
                      className="w-full rounded-t-md bg-gradient-to-t from-primary to-cyan-500 opacity-80 transition-all hover:opacity-100"
                      style={{ height: `${height}%` }}
                    />
                    <span className="text-[10px] text-muted-foreground">{d.day}</span>
                  </div>
                );
              })}
            </div>
          </motion.div>

          {/* Recent activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-2 rounded-2xl border border-border/40 bg-card/60 p-6"
          >
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" />
                <h2 className="font-semibold">Recent Activity</h2>
              </div>
            </div>
            <div className="space-y-3">
              {recentActivity.map((item) => (
                <div key={item.label} className="flex items-center gap-3 p-3 rounded-xl hover:bg-muted/40 transition-colors">
                  <span className="text-lg">{item.icon}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.label}</p>
                    <p className="text-xs text-muted-foreground">{item.meta}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs font-semibold text-emerald-500">{item.points}</p>
                    <p className="text-xs text-muted-foreground">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
