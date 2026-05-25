"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sidebar } from "@/components/layout/sidebar";
import {
  Send, Brain, Zap, Code2, Lightbulb, BookOpen,
  Paperclip, Mic, RotateCcw, ThumbsUp, ThumbsDown,
  Copy, ChevronDown, Sparkles, MessageSquare
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

const suggestions = [
  { icon: Code2, label: "Explain closures in JS", text: "Explain JavaScript closures with real-world examples" },
  { icon: BookOpen, label: "What is Big O notation?", text: "What is Big O notation? Explain with simple examples" },
  { icon: Lightbulb, label: "Debug my code", text: "Help me debug my Python code" },
  { icon: Brain, label: "System design basics", text: "Explain system design fundamentals for beginners" },
];

const initialMessages: Message[] = [
  {
    id: "1",
    role: "assistant",
    content: `# Hi! I'm your AI Mentor 👋

I'm here to help you learn anything technical — from basic syntax to advanced system design. Ask me anything!

I can help you with:
- **Explaining concepts** using real-life analogies
- **Debugging your code** step-by-step
- **Designing systems** and architecture decisions
- **Preparing for interviews** with practice questions
- **Building projects** with guided walkthroughs

What would you like to learn today?`,
    timestamp: new Date(),
  },
];

export default function MentorPage() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState("gpt-4o");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const simulateResponse = async (userMessage: string) => {
    const responses: Record<string, string> = {
      default: `Great question! Let me explain this clearly.

Think of it like this — imagine you're building with LEGO blocks. Each concept in programming is like a specific type of block.

**Key points:**
1. Start with the foundation — understand the "why" before the "how"
2. Practice with real examples, not just theory
3. Build small projects to solidify your understanding

**Code example:**
\`\`\`python
# This illustrates the concept clearly
def example():
    result = []
    for item in range(10):
        result.append(item ** 2)
    return result
\`\`\`

Does this make sense? Ask me to go deeper on any part!`,
    };

    const lower = userMessage.toLowerCase();
    if (lower.includes("closure")) {
      return `## JavaScript Closures 🔒

Think of a closure like a **function with a backpack**.

When a function is created inside another function, it can carry variables from the outer function in its "backpack" — even after the outer function has finished running!

\`\`\`javascript
function createCounter() {
  let count = 0; // This goes in the backpack!

  return function increment() {
    count++; // Accesses backpack variable
    return count;
  };
}

const counter = createCounter();
console.log(counter()); // 1
console.log(counter()); // 2  ← Still remembers count!
\`\`\`

**Real-world use case:** Event handlers in React components:
\`\`\`javascript
function Button({ label }) {
  let clicks = 0;

  return (
    <button onClick={() => {
      clicks++; // closure over 'clicks'
      console.log(\`Clicked \${clicks} times\`);
    }}>
      {label}
    </button>
  );
}
\`\`\`

**Why closures matter:**
- Data privacy (like private variables)
- State persistence without global variables
- Function factories and currying
- React hooks work because of closures!

Want me to show you more advanced closure patterns?`;
    }

    return responses.default;
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };
    const userInput = input.trim();
    setInput("");
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    await new Promise((r) => setTimeout(r, 800 + Math.random() * 600));
    const responseText = await simulateResponse(userInput);

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: responseText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <div className="flex items-center justify-between border-b border-border/40 bg-card/40 px-5 py-3">
          <div className="flex items-center gap-3">
            <div className="relative flex h-9 w-9 items-center justify-center rounded-full bg-primary/10">
              <Brain className="h-4.5 w-4.5 text-primary" />
              <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-500 border-2 border-background" />
            </div>
            <div>
              <p className="font-semibold text-sm">Nexus AI Mentor</p>
              <p className="text-xs text-emerald-500">Online · Powered by GPT-4o</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 rounded-lg bg-muted/60 border border-border/40 p-0.5">
              {["gpt-4o", "gpt-4o-mini", "claude-3.5"].map((m) => (
                <button
                  key={m}
                  onClick={() => setModel(m)}
                  className={cn(
                    "px-2.5 py-1 rounded-md text-xs font-medium transition-colors",
                    model === m ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"
                  )}
                >
                  {m}
                </button>
              ))}
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs"
              onClick={() => setMessages(initialMessages)}
            >
              <RotateCcw className="h-3.5 w-3.5 mr-1" />
              Clear
            </Button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                  "flex gap-3",
                  message.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                {message.role === "assistant" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 mt-1">
                    <Zap className="h-3.5 w-3.5 text-primary" />
                  </div>
                )}
                <div className={cn(
                  "max-w-[85%]",
                  message.role === "user"
                    ? "rounded-2xl rounded-br-sm bg-primary px-4 py-3 text-sm text-primary-foreground"
                    : "rounded-2xl rounded-bl-sm border border-border/40 bg-card/80 px-5 py-4"
                )}>
                  {message.role === "assistant" ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-foreground">
                        {message.content}
                      </pre>
                    </div>
                  ) : (
                    <p className="text-sm">{message.content}</p>
                  )}

                  {message.role === "assistant" && (
                    <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border/30">
                      <button className="text-muted-foreground hover:text-foreground transition-colors">
                        <ThumbsUp className="h-3.5 w-3.5" />
                      </button>
                      <button className="text-muted-foreground hover:text-foreground transition-colors">
                        <ThumbsDown className="h-3.5 w-3.5" />
                      </button>
                      <button className="text-muted-foreground hover:text-foreground transition-colors">
                        <Copy className="h-3.5 w-3.5" />
                      </button>
                      <span className="text-xs text-muted-foreground ml-auto">
                        {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>
                  )}
                </div>
                {message.role === "user" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 text-white text-xs font-bold mt-1">
                    S
                  </div>
                )}
              </motion.div>
            ))}

            {loading && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3"
              >
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                  <Zap className="h-3.5 w-3.5 text-primary" />
                </div>
                <div className="rounded-2xl rounded-bl-sm border border-border/40 bg-card/80 px-5 py-4">
                  <div className="flex items-center gap-1.5">
                    {[0, 150, 300].map((delay) => (
                      <div
                        key={delay}
                        className="h-2 w-2 rounded-full bg-muted-foreground/50 animate-bounce"
                        style={{ animationDelay: `${delay}ms` }}
                      />
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* Suggestion chips */}
        {messages.length <= 1 && (
          <div className="max-w-3xl mx-auto w-full px-4 pb-3">
            <div className="flex gap-2 flex-wrap justify-center">
              {suggestions.map((s) => (
                <button
                  key={s.label}
                  onClick={() => setInput(s.text)}
                  className="flex items-center gap-1.5 rounded-xl border border-border/60 bg-card/60 px-3 py-2 text-xs font-medium text-muted-foreground hover:text-foreground hover:border-border transition-colors"
                >
                  <s.icon className="h-3.5 w-3.5" />
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="border-t border-border/40 bg-card/40 px-4 py-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-end gap-2 rounded-2xl border border-border/60 bg-muted/30 p-3 focus-within:border-primary/40 transition-colors">
              <div className="flex items-center gap-1 shrink-0">
                <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-foreground">
                  <Paperclip className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-foreground">
                  <Code2 className="h-4 w-4" />
                </Button>
              </div>
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask your AI mentor anything... (Shift+Enter for newline)"
                className="flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted-foreground min-h-[36px] max-h-32 leading-relaxed"
                rows={1}
                style={{ height: "auto" }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = "auto";
                  target.style.height = Math.min(target.scrollHeight, 128) + "px";
                }}
              />
              <Button
                size="icon"
                className="h-8 w-8 shrink-0 rounded-xl bg-primary hover:bg-primary/90"
                onClick={sendMessage}
                disabled={!input.trim() || loading}
              >
                <Send className="h-3.5 w-3.5" />
              </Button>
            </div>
            <p className="text-center text-xs text-muted-foreground mt-2">
              AI can make mistakes. Always verify important information.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
