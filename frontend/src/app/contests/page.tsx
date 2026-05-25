"use client";

import { motion } from "framer-motion";
import { Sidebar } from "@/components/layout/sidebar";
import {
  Trophy, Clock, Users, Flame, ArrowRight, Calendar,
  Zap, Star, ChevronRight, BarChart2, Medal
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import Link from "next/link";

const contests = [
  {
    id: "weekly-45",
    title: "Weekly Contest #45",
    status: "live",
    startsIn: null,
    endsIn: "1h 23m",
    duration: "90 min",
    participants: 2341,
    problems: 4,
    type: "individual",
    difficulty: "Mixed",
  },
  {
    id: "biweekly-22",
    title: "Biweekly Contest #22",
    status: "upcoming",
    startsIn: "2d 4h",
    endsIn: null,
    duration: "90 min",
    participants: 856,
    problems: 4,
    type: "individual",
    difficulty: "Mixed",
  },
  {
    id: "ai-challenge-3",
    title: "AI Engineering Challenge #3",
    status: "upcoming",
    startsIn: "5d 12h",
    endsIn: null,
    duration: "3 hours",
    participants: 412,
    problems: 5,
    type: "team",
    difficulty: "Hard",
  },
  {
    id: "weekly-44",
    title: "Weekly Contest #44",
    status: "ended",
    startsIn: null,
    endsIn: null,
    duration: "90 min",
    participants: 3124,
    problems: 4,
    type: "individual",
    difficulty: "Mixed",
    myRank: 284,
  },
];

const leaderboard = [
  { rank: 1, name: "algorithmPro", score: 3450, solved: 4, time: "42:15", country: "🇮🇳" },
  { rank: 2, name: "codeNinja_rx", score: 3200, solved: 4, time: "51:33", country: "🇺🇸" },
  { rank: 3, name: "byteMaster", score: 2980, solved: 3, time: "32:10", country: "🇨🇳" },
  { rank: 4, name: "stackOverflow", score: 2760, solved: 3, time: "38:45", country: "🇷🇺" },
  { rank: 127, name: "You", score: 1840, solved: 2, time: "75:20", country: "🇮🇳", isMe: true },
];

const statusBadge = {
  live: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
  upcoming: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  ended: "bg-muted text-muted-foreground border-border/40",
};

export default function ContestsPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6 lg:p-8">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight mb-1">Contests</h1>
              <p className="text-muted-foreground text-sm">Compete globally, improve your ranking, win prizes</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="rounded-xl border border-border/40 bg-card/60 px-3 py-2 text-center">
                <p className="text-lg font-bold gradient-text">#1,284</p>
                <p className="text-xs text-muted-foreground">Your Rank</p>
              </div>
            </div>
          </div>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Contests list */}
          <div className="lg:col-span-2 space-y-4">
            {/* Live contest banner */}
            <motion.div
              initial={{ opacity: 0, scale: 0.99 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative rounded-2xl overflow-hidden border border-emerald-500/30 bg-gradient-to-br from-emerald-500/10 to-background p-6"
            >
              <div className="absolute top-3 right-3 flex items-center gap-1.5">
                <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs font-medium text-emerald-500">LIVE NOW</span>
              </div>
              <div className="flex items-start justify-between flex-wrap gap-4">
                <div>
                  <h2 className="text-xl font-bold mb-1">Weekly Contest #45</h2>
                  <p className="text-muted-foreground text-sm mb-3">Ends in <span className="font-semibold text-foreground">1h 23m</span> · 4 problems · 2,341 participants</p>
                  <div className="flex gap-2">
                    <Badge variant="outline" className="text-xs">Individual</Badge>
                    <Badge variant="outline" className="text-xs">Mixed Difficulty</Badge>
                  </div>
                </div>
                <Button className="bg-emerald-500 hover:bg-emerald-600 text-white gap-2">
                  <Zap className="h-4 w-4" />
                  Join Contest
                </Button>
              </div>

              {/* Timer progress */}
              <div className="mt-4">
                <div className="flex justify-between text-xs text-muted-foreground mb-1.5">
                  <span>Time elapsed</span>
                  <span>22 min / 90 min</span>
                </div>
                <div className="h-2 rounded-full bg-muted/60">
                  <div className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all" style={{ width: "24%" }} />
                </div>
              </div>
            </motion.div>

            {/* Other contests */}
            {contests.slice(1).map((contest, i) => (
              <motion.div
                key={contest.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 + 0.1 }}
                className="rounded-2xl border border-border/40 bg-card/60 p-5 hover:border-border transition-colors"
              >
                <div className="flex items-start justify-between flex-wrap gap-3">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold">{contest.title}</h3>
                      <Badge className={cn("text-xs border capitalize", statusBadge[contest.status as keyof typeof statusBadge])}>
                        {contest.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                      {contest.startsIn && <span>Starts in <strong className="text-foreground">{contest.startsIn}</strong></span>}
                      <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{contest.duration}</span>
                      <span className="flex items-center gap-1"><Users className="h-3 w-3" />{contest.participants} registered</span>
                      <span>{contest.problems} problems</span>
                    </div>
                    {contest.myRank && (
                      <div className="mt-2 flex items-center gap-1.5 text-xs">
                        <Medal className="h-3 w-3 text-amber-500" />
                        <span>Your rank: <strong className="text-amber-500">#{contest.myRank}</strong></span>
                      </div>
                    )}
                  </div>
                  <Button
                    variant={contest.status === "ended" ? "ghost" : "outline"}
                    size="sm"
                    className="h-8 rounded-lg text-xs"
                  >
                    {contest.status === "upcoming" ? "Register" : contest.status === "ended" ? "View Results" : "Join"}
                    <ChevronRight className="h-3 w-3 ml-1" />
                  </Button>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Leaderboard */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="rounded-2xl border border-border/40 bg-card/60 overflow-hidden"
          >
            <div className="flex items-center gap-2 p-4 border-b border-border/40">
              <Trophy className="h-4 w-4 text-amber-500" />
              <h2 className="font-semibold text-sm">Weekly #45 — Live Rankings</h2>
            </div>
            <div className="divide-y divide-border/40">
              {leaderboard.map((entry, i) => (
                <div
                  key={entry.rank}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3",
                    entry.isMe && "bg-primary/5"
                  )}
                >
                  <div className={cn(
                    "w-6 text-center text-xs font-bold",
                    entry.rank === 1 ? "text-amber-400" :
                    entry.rank === 2 ? "text-slate-400" :
                    entry.rank === 3 ? "text-amber-700" :
                    "text-muted-foreground"
                  )}>
                    {entry.rank <= 3 ? ["🥇", "🥈", "🥉"][entry.rank - 1] : `#${entry.rank}`}
                  </div>
                  <span className="text-base">{entry.country}</span>
                  <div className="flex-1 min-w-0">
                    <p className={cn("text-sm font-medium truncate", entry.isMe && "text-primary")}>
                      {entry.name} {entry.isMe && "(You)"}
                    </p>
                    <p className="text-xs text-muted-foreground">{entry.solved} solved · {entry.time}</p>
                  </div>
                  <span className="text-sm font-semibold text-muted-foreground">{entry.score}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
