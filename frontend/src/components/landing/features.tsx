"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import {
  Brain, Code2, Terminal, Cpu, Trophy, BookOpen, Map, Zap,
  MessageSquare, BarChart2, Users, FlaskConical
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Mentor",
    description: "Your personal AI teacher that explains concepts using real-life analogies, storytelling, and adaptive teaching styles.",
    color: "text-violet-400",
    bg: "bg-violet-500/10",
    border: "border-violet-500/20",
  },
  {
    icon: Code2,
    title: "Smart Code Editor",
    description: "Monaco-powered editor with AI auto-complete, real-time hints, optimization suggestions, and test case runner.",
    color: "text-cyan-400",
    bg: "bg-cyan-500/10",
    border: "border-cyan-500/20",
  },
  {
    icon: Map,
    title: "Adaptive Roadmaps",
    description: "Personalized learning paths from beginner to expert. AI analyzes your progress and adjusts the roadmap dynamically.",
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
  },
  {
    icon: Terminal,
    title: "DevOps Labs",
    description: "Real cloud environments for Docker, Kubernetes, CI/CD. Practice on actual infrastructure, not simulations.",
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
  },
  {
    icon: Cpu,
    title: "System Design Canvas",
    description: "Drag-and-drop architecture builder with live traffic simulation, scaling visualizations, and AI feedback.",
    color: "text-rose-400",
    bg: "bg-rose-500/10",
    border: "border-rose-500/20",
  },
  {
    icon: FlaskConical,
    title: "AI/ML Playground",
    description: "Experiment with LLMs, build RAG pipelines, visualize embeddings, and train models interactively.",
    color: "text-purple-400",
    bg: "bg-purple-500/10",
    border: "border-purple-500/20",
  },
  {
    icon: Trophy,
    title: "Live Contests",
    description: "Global coding competitions with real-time leaderboards, collaborative rooms, and prize pools.",
    color: "text-yellow-400",
    bg: "bg-yellow-500/10",
    border: "border-yellow-500/20",
  },
  {
    icon: BarChart2,
    title: "Progress Analytics",
    description: "Deep insights into your learning patterns, weak spots, time spent, and improvement trajectory.",
    color: "text-blue-400",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
  },
  {
    icon: Users,
    title: "Collaborative Learning",
    description: "Pair programming, code reviews, discussions, and a community of 50,000+ engineers.",
    color: "text-teal-400",
    bg: "bg-teal-500/10",
    border: "border-teal-500/20",
  },
];

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.07, duration: 0.5, ease: "easeOut" },
  }),
};

export function FeaturesSection() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section className="py-24 bg-background" ref={ref}>
      <div className="container mx-auto px-4 max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-muted/40 px-4 py-1.5 mb-4">
            <Zap className="h-3.5 w-3.5 text-primary" />
            <span className="text-sm font-medium text-muted-foreground">Everything you need</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">
            A complete ecosystem<br />
            <span className="gradient-text">for every engineer</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Not just another coding platform. NexusLearn AI combines every tool you need to go from beginner to
            professional in any modern technical domain.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              custom={i}
              variants={cardVariants}
              initial="hidden"
              animate={inView ? "visible" : "hidden"}
              className={`group relative p-6 rounded-2xl border ${feature.border} bg-card/60 card-hover cursor-default overflow-hidden`}
            >
              {/* Glow on hover */}
              <div className={`absolute inset-0 ${feature.bg} opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl`} />

              <div className={`relative z-10 flex h-11 w-11 items-center justify-center rounded-xl ${feature.bg} border ${feature.border} mb-4`}>
                <feature.icon className={`h-5 w-5 ${feature.color}`} />
              </div>
              <h3 className="relative z-10 text-base font-semibold mb-2">{feature.title}</h3>
              <p className="relative z-10 text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
