"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef, useState, useEffect } from "react";
import { Brain, Zap, ArrowRight, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const conversation = [
  {
    role: "user",
    text: "Explain closures in JavaScript like I'm a beginner",
  },
  {
    role: "ai",
    text: `Think of a closure like a **backpack** 🎒

When you create a function inside another function, the inner function gets to carry a "backpack" with all the variables from its parent function — even after the parent finishes running.

Here's a real example:
\`\`\`javascript
function makeCounter() {
  let count = 0; // in the backpack!

  return function() {
    count++;
    return count;
  }
}

const counter = makeCounter();
counter(); // 1
counter(); // 2 (remembers count!)
\`\`\`

The inner function **remembers** \`count\` even though \`makeCounter\` has finished. That's the closure! 🔒`,
  },
  {
    role: "user",
    text: "Can you give me a real-world use case?",
  },
];

export function AIMentorPreview() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });
  const [visibleMessages, setVisibleMessages] = useState(0);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!inView) return;
    let i = 0;
    const interval = setInterval(() => {
      i++;
      if (i < conversation.length) {
        setIsTyping(true);
        setTimeout(() => {
          setIsTyping(false);
          setVisibleMessages(i + 1);
        }, 800);
      } else {
        clearInterval(interval);
      }
    }, 1800);
    setVisibleMessages(1);
    return () => clearInterval(interval);
  }, [inView]);

  return (
    <section className="py-24 bg-muted/20" ref={ref}>
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: Chat UI */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="order-2 lg:order-1"
          >
            <div className="gradient-border rounded-2xl overflow-hidden bg-card/60 shadow-xl shadow-black/20">
              {/* Chat header */}
              <div className="flex items-center gap-3 border-b border-border/40 px-4 py-3">
                <div className="relative flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                  <Brain className="h-4 w-4 text-primary" />
                  <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-500 border-2 border-background" />
                </div>
                <div>
                  <p className="text-sm font-semibold">Nexus AI Mentor</p>
                  <p className="text-xs text-emerald-500">Online · GPT-4o</p>
                </div>
              </div>

              {/* Messages */}
              <div className="p-4 space-y-4 min-h-[340px] max-h-[400px] overflow-y-auto scrollbar-thin">
                {conversation.slice(0, visibleMessages).map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {msg.role === "ai" && (
                      <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 mr-2 mt-1">
                        <Zap className="h-3 w-3 text-primary" />
                      </div>
                    )}
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                        msg.role === "user"
                          ? "bg-primary text-primary-foreground rounded-br-sm"
                          : "bg-muted border border-border/40 rounded-bl-sm"
                      }`}
                    >
                      {msg.role === "ai" ? (
                        <div className="prose prose-sm dark:prose-invert max-w-none">
                          <p className="text-sm leading-relaxed whitespace-pre-wrap text-foreground">{msg.text}</p>
                        </div>
                      ) : (
                        <p>{msg.text}</p>
                      )}
                    </div>
                  </motion.div>
                ))}

                {isTyping && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-2"
                  >
                    <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10">
                      <Zap className="h-3 w-3 text-primary" />
                    </div>
                    <div className="rounded-2xl rounded-bl-sm bg-muted border border-border/40 px-4 py-3">
                      <div className="flex items-center gap-1">
                        {[0, 150, 300].map((delay) => (
                          <div
                            key={delay}
                            className="h-1.5 w-1.5 rounded-full bg-muted-foreground animate-bounce"
                            style={{ animationDelay: `${delay}ms` }}
                          />
                        ))}
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Input */}
              <div className="border-t border-border/40 p-3">
                <div className="flex items-center gap-2 rounded-xl bg-muted/60 border border-border/40 px-3 py-2">
                  <input
                    className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
                    placeholder="Ask anything about code or concepts..."
                    readOnly
                  />
                  <Button size="icon" className="h-7 w-7 rounded-lg bg-primary hover:bg-primary/90">
                    <Send className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right: copy */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="order-1 lg:order-2"
          >
            <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-muted/40 px-4 py-1.5 mb-5">
              <Brain className="h-3.5 w-3.5 text-primary" />
              <span className="text-sm font-medium text-muted-foreground">AI Mentor</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight leading-tight mb-5">
              Your AI teacher<br />
              <span className="gradient-text">available 24/7</span>
            </h2>
            <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
              Get instant, personalized explanations for any concept. The AI adapts to your level —
              using analogies, real-world examples, and step-by-step walkthroughs.
            </p>
            <ul className="space-y-3 mb-8">
              {[
                "Explains with stories, analogies, and real examples",
                "Adapts complexity to your current skill level",
                "Debugs your code and explains every error",
                "Generates custom practice problems for you",
                "Supports voice, code, files, and images",
              ].map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm text-muted-foreground">
                  <div className="h-4 w-4 rounded-full bg-primary/10 flex items-center justify-center mt-0.5 shrink-0">
                    <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                  </div>
                  {item}
                </li>
              ))}
            </ul>
            <Link href="/mentor">
              <Button size="lg" className="h-11 rounded-xl group">
                Try AI Mentor Free
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
