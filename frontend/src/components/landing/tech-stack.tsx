"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";

const categories = [
  {
    label: "Languages",
    color: "border-violet-500/30 bg-violet-500/5 text-violet-400",
    items: ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "Kotlin"],
  },
  {
    label: "Frontend",
    color: "border-cyan-500/30 bg-cyan-500/5 text-cyan-400",
    items: ["React", "Next.js", "Vue", "Angular", "TailwindCSS", "Three.js", "Svelte"],
  },
  {
    label: "Backend",
    color: "border-emerald-500/30 bg-emerald-500/5 text-emerald-400",
    items: ["FastAPI", "Django", "Node.js", "Spring Boot", "NestJS", "GraphQL", "gRPC"],
  },
  {
    label: "DevOps",
    color: "border-amber-500/30 bg-amber-500/5 text-amber-400",
    items: ["Docker", "Kubernetes", "AWS", "Terraform", "GitHub Actions", "Prometheus", "CI/CD"],
  },
  {
    label: "AI / ML",
    color: "border-rose-500/30 bg-rose-500/5 text-rose-400",
    items: ["LangChain", "PyTorch", "TensorFlow", "RAG", "Fine-tuning", "LangGraph", "Agents"],
  },
  {
    label: "Databases",
    color: "border-blue-500/30 bg-blue-500/5 text-blue-400",
    items: ["PostgreSQL", "Redis", "MongoDB", "Elasticsearch", "Qdrant", "Cassandra"],
  },
];

export function TechStackSection() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section className="py-24 bg-muted/20" ref={ref}>
      <div className="container mx-auto px-4 max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-3">
            Learn <span className="gradient-text">every modern technology</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-xl mx-auto">
            From first print statement to production deployments across 30+ tech domains.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {categories.map((cat, ci) => (
            <motion.div
              key={cat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: ci * 0.08 }}
              className="rounded-2xl border border-border/40 bg-card/50 p-5"
            >
              <div className={`inline-flex items-center rounded-lg border px-2.5 py-1 text-xs font-semibold mb-4 ${cat.color}`}>
                {cat.label}
              </div>
              <div className="flex flex-wrap gap-2">
                {cat.items.map((item) => (
                  <span
                    key={item}
                    className="rounded-lg bg-muted/60 border border-border/40 px-2.5 py-1 text-xs font-medium text-muted-foreground hover:text-foreground hover:border-border transition-colors"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
