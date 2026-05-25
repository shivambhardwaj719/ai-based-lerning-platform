"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Sidebar } from "@/components/layout/sidebar";
import {
  ChevronLeft, Brain, BookOpen, Code2, HelpCircle, Bookmark,
  CheckCircle2, ChevronRight, Lightbulb, Volume2, Share2,
  RotateCcw, Zap, Clock, Star, Play
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import Link from "next/link";

const sections = [
  {
    id: "intro",
    title: "What is OOP?",
    type: "concept",
    content: `Object-Oriented Programming (OOP) is a way of writing code by thinking in **objects** — just like the real world.

Imagine you're describing a "Car" to someone. You'd say:
- It has **properties**: color, model, speed, fuel
- It can **do things**: start, stop, accelerate, brake

In OOP, a **class** is the blueprint, and an **object** is a real instance of that blueprint.

\`\`\`python
class Car:
    def __init__(self, brand, color):
        self.brand = brand  # Property
        self.color = color  # Property

    def start(self):       # Method (behavior)
        print(f"{self.brand} is starting!")

# Creating objects (instances)
my_car = Car("Tesla", "Red")
my_car.start()  # Tesla is starting!
\`\`\`

**Real-life analogy**: Think of a class as a cookie cutter and objects as the cookies. The cutter defines the shape, but each cookie can have different decorations!`,
  },
  {
    id: "inheritance",
    title: "Inheritance",
    type: "concept",
    content: `Inheritance lets you create a new class that **inherits** properties and methods from an existing class.

Think of it like genetics — a child inherits traits from parents, but can also have their own unique traits.

\`\`\`python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass  # Will be overridden

class Dog(Animal):  # Dog inherits from Animal
    def speak(self):
        return f"{self.name} says: Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says: Meow!"

dog = Dog("Buddy")
cat = Cat("Whiskers")

print(dog.speak())  # Buddy says: Woof!
print(cat.speak())  # Whiskers says: Meow!
\`\`\`

**Why use inheritance?**
- Avoid repeating code (DRY principle)
- Create hierarchical relationships
- Override only what's different`,
  },
  {
    id: "quiz",
    title: "Quick Quiz",
    type: "quiz",
    question: "What keyword is used in Python to inherit from a parent class?",
    options: ["extends", "inherits", "(ParentClass)", "super"],
    correct: 2,
  },
];

const tableOfContents = [
  { id: "intro", label: "What is OOP?", done: true },
  { id: "inheritance", label: "Inheritance", done: false, active: true },
  { id: "polymorphism", label: "Polymorphism", done: false },
  { id: "encapsulation", label: "Encapsulation", done: false },
  { id: "quiz", label: "Chapter Quiz", done: false, type: "quiz" },
];

export default function TopicPage() {
  const [activeSection, setActiveSection] = useState(1);
  const [mode, setMode] = useState<"beginner" | "advanced">("beginner");
  const [quizAnswer, setQuizAnswer] = useState<number | null>(null);
  const [bookmarked, setBookmarked] = useState(false);

  const section = sections[activeSection] || sections[1];

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex overflow-hidden">
        {/* Table of contents */}
        <aside className="hidden lg:flex w-64 shrink-0 flex-col border-r border-border/40 bg-card/30 overflow-y-auto scrollbar-thin">
          <div className="p-4 border-b border-border/40">
            <Link href="/learn" className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-3">
              <ChevronLeft className="h-3.5 w-3.5" />
              Back to Topics
            </Link>
            <h2 className="font-semibold text-sm">OOP in Python</h2>
            <div className="mt-2">
              <div className="flex justify-between text-xs text-muted-foreground mb-1">
                <span>Progress</span>
                <span>1/5</span>
              </div>
              <Progress value={20} className="h-1.5" />
            </div>
          </div>

          <nav className="p-3 space-y-1 flex-1">
            {tableOfContents.map((item, i) => (
              <button
                key={item.id}
                onClick={() => setActiveSection(i)}
                className={cn(
                  "w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-left transition-colors text-sm",
                  activeSection === i
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/40"
                )}
              >
                {item.done ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                ) : item.type === "quiz" ? (
                  <HelpCircle className="h-4 w-4 shrink-0" />
                ) : (
                  <div className={cn(
                    "h-4 w-4 rounded-full border-2 shrink-0",
                    activeSection === i ? "border-primary" : "border-border"
                  )} />
                )}
                <span className="truncate">{item.label}</span>
              </button>
            ))}
          </nav>

          {/* AI Ask panel */}
          <div className="p-3 border-t border-border/40">
            <Link href="/mentor">
              <Button className="w-full h-9 rounded-xl text-xs gap-2">
                <Brain className="h-3.5 w-3.5" />
                Ask AI about this topic
              </Button>
            </Link>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto scrollbar-thin">
          {/* Top bar */}
          <div className="sticky top-0 z-10 flex items-center justify-between border-b border-border/40 bg-background/90 backdrop-blur-xl px-6 py-3">
            <div className="flex items-center gap-3">
              <Badge className="text-xs bg-blue-500/10 text-blue-400 border-blue-500/20">🐍 Python · OOP</Badge>
              <div className="flex items-center gap-1 rounded-lg bg-muted/60 border border-border/40 p-0.5">
                {(["beginner", "advanced"] as const).map((m) => (
                  <button
                    key={m}
                    onClick={() => setMode(m)}
                    className={cn(
                      "px-2.5 py-1 rounded-md text-xs font-medium capitalize transition-colors",
                      mode === m ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"
                    )}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={() => setBookmarked(!bookmarked)}
              >
                <Bookmark className={cn("h-4 w-4", bookmarked ? "fill-primary text-primary" : "text-muted-foreground")} />
              </Button>
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" /> 35 min read
              </span>
            </div>
          </div>

          {/* Content */}
          <div className="max-w-3xl mx-auto px-6 py-8">
            <motion.div
              key={activeSection}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {section.type === "concept" && (
                <div>
                  <h1 className="text-2xl font-bold tracking-tight mb-6">{section.title}</h1>

                  {mode === "beginner" && (
                    <div className="rounded-xl bg-amber-500/5 border border-amber-500/20 p-4 mb-6 flex gap-3">
                      <Lightbulb className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
                      <p className="text-sm text-muted-foreground">
                        <strong className="text-foreground">Beginner tip:</strong> Don&apos;t worry about memorizing syntax right now.
                        Focus on understanding the concept first — the code will make sense as you practice!
                      </p>
                    </div>
                  )}

                  <div className="prose prose-neutral dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap text-sm leading-[1.8] font-sans text-foreground/90">
                      {section.content}
                    </pre>
                  </div>
                </div>
              )}

              {section.type === "quiz" && (
                <div>
                  <div className="flex items-center gap-2 mb-6">
                    <HelpCircle className="h-5 w-5 text-primary" />
                    <h1 className="text-2xl font-bold">Quick Quiz</h1>
                  </div>

                  <div className="rounded-2xl border border-border/40 bg-card/60 p-6">
                    <p className="font-medium mb-5 text-lg">{(section as any).question}</p>
                    <div className="space-y-3">
                      {(section as any).options.map((option: string, i: number) => (
                        <button
                          key={i}
                          onClick={() => setQuizAnswer(i)}
                          className={cn(
                            "w-full text-left rounded-xl border p-4 text-sm transition-all",
                            quizAnswer === null
                              ? "border-border/40 hover:border-primary/40 hover:bg-primary/5"
                              : i === (section as any).correct
                              ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-500"
                              : quizAnswer === i
                              ? "border-rose-500/40 bg-rose-500/10 text-rose-500"
                              : "border-border/40 opacity-60"
                          )}
                        >
                          <span className="font-mono mr-3 text-muted-foreground">
                            {String.fromCharCode(65 + i)}.
                          </span>
                          {option}
                        </button>
                      ))}
                    </div>
                    {quizAnswer !== null && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={cn(
                          "mt-4 rounded-xl p-4 text-sm",
                          quizAnswer === (section as any).correct
                            ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-500"
                            : "bg-rose-500/10 border border-rose-500/20 text-rose-500"
                        )}
                      >
                        {quizAnswer === (section as any).correct
                          ? "✅ Correct! Well done."
                          : `❌ Not quite. The correct answer is: ${(section as any).options[(section as any).correct]}`}
                      </motion.div>
                    )}
                  </div>
                </div>
              )}

              {/* Navigation */}
              <div className="flex items-center justify-between mt-10 pt-6 border-t border-border/40">
                <Button
                  variant="outline"
                  className="gap-2 rounded-xl border-border/60"
                  onClick={() => setActiveSection(Math.max(0, activeSection - 1))}
                  disabled={activeSection === 0}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <Button
                  className="gap-2 rounded-xl"
                  onClick={() => setActiveSection(Math.min(sections.length - 1, activeSection + 1))}
                >
                  {activeSection === sections.length - 1 ? "Complete" : "Next"}
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  );
}
