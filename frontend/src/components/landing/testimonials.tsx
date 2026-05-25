"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { Quote } from "lucide-react";

const testimonials = [
  {
    quote: "NexusLearn AI literally changed how I learn. The AI mentor explains things better than any professor I've had. Went from zero to landing a ₹25 LPA job in 8 months.",
    name: "Priya Sharma",
    role: "SDE @ Amazon",
    avatar: "PS",
    gradient: "from-violet-500 to-purple-600",
    rating: 5,
  },
  {
    quote: "The DevOps labs are insane. Real Kubernetes clusters, actual Docker environments. You're not just reading — you're doing. Got AWS certified in 6 weeks.",
    name: "Arjun Mehta",
    role: "DevOps Engineer @ Microsoft",
    avatar: "AM",
    gradient: "from-cyan-500 to-blue-600",
    rating: 5,
  },
  {
    quote: "I tried Udemy, Coursera, LeetCode separately. NexusLearn has everything in one place with an AI that actually understands your doubts. Worth every rupee.",
    name: "Shreya Patel",
    role: "Full Stack Developer @ Flipkart",
    avatar: "SP",
    gradient: "from-emerald-500 to-teal-600",
    rating: 5,
  },
  {
    quote: "The roadmap feature is gold. It doesn't overwhelm you — just shows you exactly what to learn next. My system design improved massively in 3 months.",
    name: "Rohan Gupta",
    role: "Senior SDE @ Google",
    avatar: "RG",
    gradient: "from-amber-500 to-orange-600",
    rating: 5,
  },
  {
    quote: "AI/ML content here is actually practical. You're building RAG systems and LangChain agents from day one, not just theory. Got my first AI role with this.",
    name: "Ananya Singh",
    role: "ML Engineer @ OpenAI",
    avatar: "AS",
    gradient: "from-rose-500 to-pink-600",
    rating: 5,
  },
  {
    quote: "Contest feature keeps me sharp. The real-time leaderboard and collaborative rooms make it feel like a real hackathon. Improved my speed dramatically.",
    name: "Karan Verma",
    role: "Competitive Programmer",
    avatar: "KV",
    gradient: "from-indigo-500 to-violet-600",
    rating: 5,
  },
];

export function TestimonialsSection() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section className="py-24 bg-background overflow-hidden" ref={ref}>
      <div className="container mx-auto px-4 max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          className="text-center mb-14"
        >
          <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-3">
            Engineers who{" "}
            <span className="gradient-text">made it happen</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-xl mx-auto">
            Join 50,000+ engineers who leveled up with NexusLearn AI.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.08, duration: 0.5 }}
              className="group relative rounded-2xl border border-border/40 bg-card/60 p-6 card-hover"
            >
              <Quote className="h-8 w-8 text-primary/20 mb-4" />
              <p className="text-sm text-muted-foreground leading-relaxed mb-6">{`"${t.quote}"`}</p>
              <div className="flex items-center gap-3 mt-auto">
                <div className={`flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br ${t.gradient} text-white text-xs font-bold shrink-0`}>
                  {t.avatar}
                </div>
                <div>
                  <p className="text-sm font-semibold">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.role}</p>
                </div>
                <div className="ml-auto flex">
                  {[...Array(t.rating)].map((_, j) => (
                    <span key={j} className="text-amber-400 text-xs">★</span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
