"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import { Sidebar } from "@/components/layout/sidebar";
import {
  Play, ChevronLeft, Lightbulb, RotateCcw, CheckCircle2,
  XCircle, Brain, ChevronRight, Code2, Clock, Zap,
  SplitSquareHorizontal, BookOpen
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import Link from "next/link";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

const starterCode = {
  python: `class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        # Your solution here
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
`,
  javascript: `/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number[]}
 */
var twoSum = function(nums, target) {
    // Your solution here
    const seen = {};
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        if (complement in seen) return [seen[complement], i];
        seen[nums[i]] = i;
    }
    return [];
};`,
  java: `class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Your solution here
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (seen.containsKey(complement)) {
                return new int[]{seen.get(complement), i};
            }
            seen.put(nums[i], i);
        }
        return new int[]{};
    }
}`,
};

const testCases = [
  { input: "nums = [2,7,11,15], target = 9", expected: "[0,1]", output: "[0,1]", status: "pass" },
  { input: "nums = [3,2,4], target = 6", expected: "[1,2]", output: "[1,2]", status: "pass" },
  { input: "nums = [3,3], target = 6", expected: "[0,1]", output: "[0,1]", status: "pass" },
];

const hints = [
  "Try using a hash map to store numbers you've seen so far.",
  "For each number, check if its complement (target - current) is in the hash map.",
  "This gives you O(n) time complexity — much better than O(n²) brute force.",
];

export default function ProblemPage() {
  const [lang, setLang] = useState<"python" | "javascript" | "java">("python");
  const [code, setCode] = useState(starterCode.python);
  const [activeTab, setActiveTab] = useState<"description" | "solution" | "discussion">("description");
  const [consoleTab, setConsoleTab] = useState<"testcases" | "results">("testcases");
  const [running, setRunning] = useState(false);
  const [ran, setRan] = useState(false);
  const [hintIndex, setHintIndex] = useState(-1);
  const [showAI, setShowAI] = useState(false);

  const handleRun = async () => {
    setRunning(true);
    await new Promise((r) => setTimeout(r, 1200));
    setRunning(false);
    setRan(true);
    setConsoleTab("results");
  };

  const handleLangChange = (newLang: "python" | "javascript" | "java") => {
    setLang(newLang);
    setCode(starterCode[newLang]);
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <div className="flex items-center justify-between border-b border-border/40 bg-card/40 px-4 py-2.5 flex-wrap gap-2">
          <div className="flex items-center gap-3">
            <Link href="/practice">
              <Button variant="ghost" size="icon" className="h-7 w-7">
                <ChevronLeft className="h-4 w-4" />
              </Button>
            </Link>
            <span className="font-semibold text-sm">1. Two Sum</span>
            <Badge className="text-xs bg-emerald-500/10 text-emerald-500 border-emerald-500/20">Easy</Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs gap-1.5"
              onClick={() => setShowAI(!showAI)}
            >
              <Brain className="h-3.5 w-3.5 text-primary" />
              AI Hint
            </Button>
            <div className="flex items-center gap-1 rounded-lg bg-muted/60 border border-border/40 p-0.5">
              {(["python", "javascript", "java"] as const).map((l) => (
                <button
                  key={l}
                  onClick={() => handleLangChange(l)}
                  className={cn(
                    "px-2.5 py-1 rounded-md text-xs font-medium transition-colors capitalize",
                    lang === l ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"
                  )}
                >
                  {l === "javascript" ? "JS" : l === "java" ? "Java" : "Python"}
                </button>
              ))}
            </div>
            <Button
              size="sm"
              className="h-7 text-xs bg-primary hover:bg-primary/90 gap-1.5"
              onClick={handleRun}
              disabled={running}
            >
              {running ? (
                <div className="h-3 w-3 rounded-full border-2 border-primary-foreground/40 border-t-primary-foreground animate-spin" />
              ) : (
                <Play className="h-3 w-3" />
              )}
              {running ? "Running..." : "Run"}
            </Button>
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Left: Problem description */}
          <div className="w-[380px] border-r border-border/40 flex flex-col overflow-hidden shrink-0 hidden lg:flex">
            {/* Tabs */}
            <div className="flex border-b border-border/40 bg-muted/20">
              {(["description", "solution", "discussion"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={cn(
                    "px-4 py-2.5 text-xs font-medium capitalize transition-colors",
                    activeTab === tab
                      ? "text-foreground border-b-2 border-primary"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {tab}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-y-auto scrollbar-thin p-5">
              {activeTab === "description" && (
                <div className="space-y-5">
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <h2 className="font-bold text-base">Two Sum</h2>
                      <Badge className="text-xs bg-emerald-500/10 text-emerald-500 border-emerald-500/20">Easy</Badge>
                    </div>
                    <div className="flex gap-2 mb-4 flex-wrap">
                      {["Array", "Hash Table"].map((t) => (
                        <Badge key={t} variant="outline" className="text-xs border-border/40">{t}</Badge>
                      ))}
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      Given an array of integers <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono text-foreground">nums</code> and
                      an integer <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono text-foreground">target</code>,
                      return indices of the two numbers such that they add up to target.
                    </p>
                    <p className="text-sm text-muted-foreground leading-relaxed mt-2">
                      You may assume that each input would have <strong className="text-foreground">exactly one solution</strong>,
                      and you may not use the same element twice.
                    </p>
                  </div>

                  {/* Examples */}
                  <div className="space-y-3">
                    {[
                      { input: "nums = [2,7,11,15], target = 9", output: "[0,1]", explanation: "nums[0] + nums[1] == 9, return [0, 1]" },
                      { input: "nums = [3,2,4], target = 6", output: "[1,2]" },
                    ].map((ex, i) => (
                      <div key={i} className="rounded-xl bg-muted/40 border border-border/40 p-4">
                        <p className="text-xs font-semibold mb-2">Example {i + 1}</p>
                        <div className="font-mono text-xs space-y-1">
                          <p><span className="text-muted-foreground">Input: </span>{ex.input}</p>
                          <p><span className="text-muted-foreground">Output: </span>{ex.output}</p>
                          {ex.explanation && (
                            <p><span className="text-muted-foreground">Explanation: </span>{ex.explanation}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Constraints */}
                  <div>
                    <p className="text-xs font-semibold mb-2">Constraints</p>
                    <ul className="space-y-1">
                      {["2 ≤ nums.length ≤ 10⁴", "-10⁹ ≤ nums[i] ≤ 10⁹", "-10⁹ ≤ target ≤ 10⁹"].map((c) => (
                        <li key={c} className="text-xs text-muted-foreground font-mono">• {c}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Hints */}
                  <div className="space-y-2">
                    <p className="text-xs font-semibold">Hints</p>
                    {hints.map((hint, i) => (
                      <div key={i}>
                        {i <= hintIndex ? (
                          <div className="rounded-xl bg-amber-500/5 border border-amber-500/20 p-3 text-xs text-muted-foreground">
                            💡 {hint}
                          </div>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-7 text-xs border-border/40 text-muted-foreground"
                            onClick={() => setHintIndex(i)}
                          >
                            <Lightbulb className="h-3 w-3 mr-1" />
                            Show Hint {i + 1}
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right: Editor + Console */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Editor */}
            <div className="flex-1 overflow-hidden">
              <MonacoEditor
                height="100%"
                language={lang === "javascript" ? "javascript" : lang}
                theme="vs-dark"
                value={code}
                onChange={(v) => v && setCode(v)}
                options={{
                  fontSize: 13,
                  minimap: { enabled: false },
                  lineNumbers: "on",
                  scrollBeyondLastLine: false,
                  wordWrap: "on",
                  formatOnPaste: true,
                  tabSize: 4,
                  padding: { top: 16, bottom: 16 },
                  fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                  fontLigatures: true,
                  smoothScrolling: true,
                  cursorBlinking: "smooth",
                }}
              />
            </div>

            {/* Console panel */}
            <div className="border-t border-border/40 bg-card/40" style={{ height: 200 }}>
              <div className="flex items-center gap-1 border-b border-border/40 px-4 bg-muted/20">
                {(["testcases", "results"] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setConsoleTab(tab)}
                    className={cn(
                      "px-3 py-2 text-xs font-medium capitalize transition-colors",
                      consoleTab === tab
                        ? "text-foreground border-b-2 border-primary"
                        : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <div className="p-4 overflow-y-auto h-[calc(100%-36px)] scrollbar-thin">
                {consoleTab === "testcases" && (
                  <div className="space-y-3">
                    {testCases.map((tc, i) => (
                      <div key={i} className="rounded-lg bg-muted/40 border border-border/40 p-3">
                        <p className="text-xs font-medium mb-1">Case {i + 1}</p>
                        <code className="text-xs text-muted-foreground block">{tc.input}</code>
                      </div>
                    ))}
                  </div>
                )}

                {consoleTab === "results" && ran && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 mb-3">
                      <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                      <span className="text-sm font-semibold text-emerald-500">All 3 test cases passed!</span>
                    </div>
                    {testCases.map((tc, i) => (
                      <div key={i} className="rounded-lg border border-border/40 p-3 bg-emerald-500/5">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium">Case {i + 1}</span>
                          <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                        </div>
                        <code className="text-xs text-muted-foreground block">Output: {tc.output}</code>
                      </div>
                    ))}
                  </div>
                )}

                {consoleTab === "results" && !ran && (
                  <p className="text-xs text-muted-foreground">Run your code to see results</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
