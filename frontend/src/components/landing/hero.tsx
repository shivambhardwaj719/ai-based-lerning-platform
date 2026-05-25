"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Play, Sparkles, Code2, Brain, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useState, useEffect } from "react";

const rotatingWords = ["Python", "React", "System Design", "DevOps", "AI/ML", "LangChain", "Kubernetes", "FastAPI"];

const codeSnippet = `# AI generates this for you
def learn_with_ai(topic: str):
    mentor = AIMentor(model="gpt-4o")
    plan = mentor.create_roadmap(topic)

    for concept in plan.concepts:
        # Explains with analogies
        explanation = mentor.explain(
            concept,
            style="storytelling",
            level="beginner"
        )
        yield explanation`;

export function HeroSection() {
  const [wordIndex, setWordIndex] = useState(0);
  const [displayText, setDisplayText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const word = rotatingWords[wordIndex];
    let timeout: ReturnType<typeof setTimeout>;

    if (!isDeleting && displayText === word) {
      timeout = setTimeout(() => setIsDeleting(true), 1800);
    } else if (isDeleting && displayText === "") {
      setIsDeleting(false);
      setWordIndex((i) => (i + 1) % rotatingWords.length);
    } else {
      const speed = isDeleting ? 60 : 100;
      timeout = setTimeout(() => {
        setDisplayText(isDeleting ? word.slice(0, displayText.length - 1) : word.slice(0, displayText.length + 1));
      }, speed);
    }
    return () => clearTimeout(timeout);
  }, [displayText, isDeleting, wordIndex]);

  return (
    <section className="relative overflow-hidden pt-20 pb-32 md:pt-28 md:pb-40">
      {/* Animated grid background */}
      <div className="absolute inset-0 z-0">
        <div
          className="absolute inset-0 opacity-[0.03] dark:opacity-[0.06]"
          style={{
            backgroundImage: `linear-gradient(oklch(0.65 0.24 270 / 50%) 1px, transparent 1px), linear-gradient(90deg, oklch(0.65 0.24 270 / 50%) 1px, transparent 1px)`,
            backgroundSize: "60px 60px",
          }}
        />
      </div>

      {/* Glow blobs */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-20 w-[700px] h-[700px] rounded-full bg-primary/8 blur-[120px] animate-pulse-glow" />
        <div className="absolute top-20 right-0 w-[500px] h-[500px] rounded-full bg-cyan-500/6 blur-[120px] animate-pulse-glow" style={{ animationDelay: "1.5s" }} />
        <div className="absolute -bottom-20 left-1/2 -translate-x-1/2 w-[800px] h-[300px] rounded-full bg-violet-500/5 blur-[100px]" />
      </div>

      <div className="container relative z-10 mx-auto px-4 max-w-7xl">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left: Copy */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 mb-6"
            >
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              <span className="text-sm text-primary font-medium">AI-Native Learning Platform</span>
            </motion.div>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.05] mb-6">
              Master{" "}
              <span className="relative">
                <span className="gradient-text">{displayText}</span>
                <span className="border-r-2 border-primary ml-0.5 animate-[blink_1s_infinite]" />
              </span>
              <br />
              <span className="text-foreground/80">with your</span>
              <br />
              <span className="gradient-text">AI Mentor</span>
            </h1>

            <p className="text-lg text-muted-foreground leading-relaxed mb-8 max-w-xl">
              The all-in-one platform combining LeetCode, Coursera, GitHub, and AI tutoring.
              Learn by doing — with real-time AI feedback, interactive labs, and personalized roadmaps.
            </p>

            <div className="flex flex-wrap gap-3 mb-10">
              <Link href="/signup">
                <Button size="lg" className="h-12 px-8 text-base font-semibold rounded-xl bg-primary hover:bg-primary/90 group">
                  Start Learning Free
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
              <Button variant="outline" size="lg" className="h-12 px-8 text-base font-semibold rounded-xl border-border/60 hover:bg-muted/60 group">
                <Play className="mr-2 h-4 w-4 text-primary group-hover:scale-110 transition-transform" />
                Watch Demo
              </Button>
            </div>

            {/* Social proof */}
            <div className="flex items-center gap-6 flex-wrap">
              <div className="flex -space-x-2">
                {["🧑‍💻", "👩‍🎓", "👨‍🔬", "👩‍💼", "🧑‍🏫"].map((emoji, i) => (
                  <div
                    key={i}
                    className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-background bg-muted text-xs"
                  >
                    {emoji}
                  </div>
                ))}
              </div>
              <div>
                <div className="flex items-center gap-1 mb-0.5">
                  {[...Array(5)].map((_, i) => (
                    <span key={i} className="text-amber-400 text-sm">★</span>
                  ))}
                  <span className="text-sm font-semibold ml-1">4.9</span>
                </div>
                <p className="text-xs text-muted-foreground">Trusted by 50,000+ engineers</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-xs">No credit card</Badge>
                <Badge variant="secondary" className="text-xs">Free tier available</Badge>
              </div>
            </div>
          </motion.div>

          {/* Right: Code card */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
            className="relative"
          >
            {/* Floating badge */}
            <motion.div
              animate={{ y: [-4, 4, -4] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -top-4 -right-4 z-10 flex items-center gap-1.5 rounded-xl border border-primary/20 bg-card/90 backdrop-blur-xl px-3 py-2 shadow-xl"
            >
              <Brain className="h-3.5 w-3.5 text-primary" />
              <span className="text-xs font-medium">AI Mentor Active</span>
            </motion.div>

            <motion.div
              animate={{ y: [4, -4, 4] }}
              transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
              className="absolute -bottom-4 -left-4 z-10 flex items-center gap-1.5 rounded-xl border border-emerald-500/20 bg-card/90 backdrop-blur-xl px-3 py-2 shadow-xl"
            >
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-medium text-emerald-500">Tests passing</span>
            </motion.div>

            {/* Code editor mockup */}
            <div className="gradient-border rounded-2xl overflow-hidden shadow-2xl shadow-black/30">
              {/* Title bar */}
              <div className="flex items-center gap-2 border-b border-border/40 bg-card/50 px-4 py-3">
                <div className="flex gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-rose-500/80" />
                  <div className="h-3 w-3 rounded-full bg-amber-500/80" />
                  <div className="h-3 w-3 rounded-full bg-emerald-500/80" />
                </div>
                <div className="flex-1 flex justify-center">
                  <div className="flex items-center gap-1.5 rounded-md bg-muted/60 px-3 py-1">
                    <Code2 className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground font-mono">ai_mentor.py</span>
                  </div>
                </div>
                <Badge className="text-[10px] bg-primary/10 text-primary border-primary/20">Python</Badge>
              </div>

              {/* Code */}
              <div className="bg-[oklch(0.07_0.012_264)] p-5 font-mono text-xs leading-relaxed overflow-hidden">
                <pre className="text-slate-300 whitespace-pre-wrap">
                  <span className="text-slate-500"># AI generates this for you{"\n"}</span>
                  <span className="text-violet-400">def </span>
                  <span className="text-cyan-300">learn_with_ai</span>
                  <span className="text-slate-300">(</span>
                  <span className="text-amber-300">topic</span>
                  <span className="text-slate-400">: str</span>
                  <span className="text-slate-300">):{"\n"}</span>
                  <span className="text-slate-300">{"    "}mentor = </span>
                  <span className="text-cyan-300">AIMentor</span>
                  <span className="text-slate-300">(model=</span>
                  <span className="text-emerald-300">"gpt-4o"</span>
                  <span className="text-slate-300">){"\n"}</span>
                  <span className="text-slate-300">{"    "}plan = mentor.</span>
                  <span className="text-cyan-300">create_roadmap</span>
                  <span className="text-slate-300">(topic){"\n\n"}</span>
                  <span className="text-violet-400">{"    "}for </span>
                  <span className="text-amber-300">concept </span>
                  <span className="text-violet-400">in </span>
                  <span className="text-slate-300">plan.concepts:{"\n"}</span>
                  <span className="text-slate-500">{"        "}# Explains with analogies{"\n"}</span>
                  <span className="text-slate-300">{"        "}explanation = mentor.</span>
                  <span className="text-cyan-300">explain</span>
                  <span className="text-slate-300">({"\n"}</span>
                  <span className="text-slate-300">{"            "}concept,{"\n"}</span>
                  <span className="text-slate-300">{"            "}style=</span>
                  <span className="text-emerald-300">"storytelling"</span>
                  <span className="text-slate-300">,{"\n"}</span>
                  <span className="text-slate-300">{"            "}level=</span>
                  <span className="text-emerald-300">"beginner"</span>
                  <span className="text-slate-300">{"\n"}</span>
                  <span className="text-slate-300">{"        "}){"\n"}</span>
                  <span className="text-violet-400">{"        "}yield </span>
                  <span className="text-slate-300">explanation</span>
                </pre>
              </div>

              {/* AI response */}
              <div className="border-t border-border/40 bg-card/50 p-4">
                <div className="flex items-start gap-3">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <Zap className="h-3 w-3 text-primary" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-muted-foreground mb-1 font-medium">AI Mentor</p>
                    <p className="text-xs text-foreground/80 leading-relaxed">
                      Think of <code className="bg-muted px-1 rounded text-primary">AIMentor</code> like having a senior engineer who explains everything using real-world stories...
                    </p>
                    <div className="mt-2 flex items-center gap-1">
                      <div className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
                      <div className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
                      <div className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
