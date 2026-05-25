"use client";

import { motion } from "framer-motion";
import { ArrowRight, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function CTASection() {
  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-4 max-w-4xl text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="relative rounded-3xl overflow-hidden p-12 md:p-16"
        >
          {/* BG */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-cyan-500/10 to-violet-500/15" />
          <div className="absolute inset-0 border border-primary/20 rounded-3xl" />
          <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-primary/10 blur-[80px]" />
          <div className="absolute -bottom-20 -left-20 w-80 h-80 rounded-full bg-cyan-500/8 blur-[80px]" />

          <div className="relative z-10">
            <div className="flex justify-center mb-5">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 border border-primary/20">
                <Zap className="h-7 w-7 text-primary" />
              </div>
            </div>
            <h2 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-4">
              Start your journey<br />
              <span className="gradient-text">today — it&apos;s free</span>
            </h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto">
              Join 50,000+ engineers learning smarter with AI.
              No credit card required. Start coding in 60 seconds.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/signup">
                <Button size="lg" className="h-13 px-10 text-lg font-semibold rounded-xl bg-primary hover:bg-primary/90 group w-full sm:w-auto">
                  Get Started Free
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link href="/roadmap">
                <Button variant="outline" size="lg" className="h-13 px-10 text-lg font-semibold rounded-xl border-border/60 hover:bg-muted/40 w-full sm:w-auto">
                  Explore Roadmaps
                </Button>
              </Link>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">
              No signup required to browse · Free tier forever available
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
