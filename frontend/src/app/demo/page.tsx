"use client";

import { Navbar } from "@/components/layout/navbar";
import { Button } from "@/components/ui/button";
import { Play, PlayCircle, ArrowRight, Code2, Network, TerminalSquare } from "lucide-react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function DemoPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto text-center mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <Badge variant="outline" className="mb-4 text-primary border-primary/30 bg-primary/5">
            Interactive Tour
          </Badge>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6">
            Experience the Future of <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500">
              Technical Education
            </span>
          </h1>
          <p className="text-lg text-muted-foreground mb-8">
            See how our AI-native platform accelerates your learning through personalized mentoring, real-time collaboration, and immersive cloud labs.
          </p>
        </div>

        {/* Video Player Mockup */}
        <div className="max-w-5xl mx-auto mb-20 animate-in fade-in zoom-in-95 duration-1000 delay-150">
          <Card className="overflow-hidden border-primary/20 shadow-2xl shadow-primary/10 bg-black aspect-video relative group flex items-center justify-center cursor-pointer">
            <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-blue-500/20 opacity-50"></div>
            
            {/* Fake Video UI Overlay */}
            <div className="absolute inset-x-0 bottom-0 p-4 bg-gradient-to-t from-black/90 to-transparent flex flex-col justify-end opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <div className="h-1.5 w-full bg-white/20 rounded-full mb-4 overflow-hidden">
                <div className="h-full bg-primary w-1/3"></div>
              </div>
              <div className="flex justify-between text-white text-sm">
                <div className="flex items-center space-x-4">
                  <Play className="h-5 w-5 hover:text-primary transition-colors" />
                  <span>01:24 / 04:15</span>
                </div>
                <div className="font-semibold tracking-wide">NEXUSLEARN OVERVIEW</div>
              </div>
            </div>

            {/* Big Play Button */}
            <div className="relative z-10 bg-background/20 backdrop-blur-md border border-white/10 p-6 rounded-full group-hover:scale-110 transition-transform duration-300 shadow-xl">
              <PlayCircle className="h-16 w-16 text-white" />
            </div>
          </Card>
        </div>

        {/* Feature Highlights Tabs */}
        <div className="max-w-4xl mx-auto mb-20 animate-in fade-in duration-1000 delay-300">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold tracking-tight">Explore the Platform</h2>
          </div>
          
          <Tabs defaultValue="editor" className="w-full">
            <TabsList className="grid w-full grid-cols-1 md:grid-cols-3 h-auto gap-4 bg-transparent">
              <TabsTrigger value="editor" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary border border-border/50 py-4 flex flex-col items-center gap-2 rounded-xl">
                <Code2 className="h-6 w-6" />
                <span className="font-semibold">AI Code Editor</span>
              </TabsTrigger>
              <TabsTrigger value="labs" className="data-[state=active]:bg-blue-500/10 data-[state=active]:text-blue-500 border border-border/50 py-4 flex flex-col items-center gap-2 rounded-xl">
                <TerminalSquare className="h-6 w-6" />
                <span className="font-semibold">Cloud Labs</span>
              </TabsTrigger>
              <TabsTrigger value="system" className="data-[state=active]:bg-purple-500/10 data-[state=active]:text-purple-500 border border-border/50 py-4 flex flex-col items-center gap-2 rounded-xl">
                <Network className="h-6 w-6" />
                <span className="font-semibold">System Design</span>
              </TabsTrigger>
            </TabsList>

            <div className="mt-8 bg-card border border-border/50 rounded-2xl p-8">
              <TabsContent value="editor" className="space-y-4 m-0">
                <h3 className="text-2xl font-bold">Smart Code Editor</h3>
                <p className="text-muted-foreground leading-relaxed text-lg">
                  Write code in our VS Code compatible Monaco editor. Our AI mentor works alongside you, explaining compilation errors, offering time-complexity optimizations, and generating tailored hints before you get fully stuck.
                </p>
                <div className="pt-4">
                  <Link href="/practice/two-sum">
                    <Button variant="outline" className="group">
                      Try the Editor <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </Link>
                </div>
              </TabsContent>
              
              <TabsContent value="labs" className="space-y-4 m-0">
                <h3 className="text-2xl font-bold">Ephemeral Cloud Sandbox</h3>
                <p className="text-muted-foreground leading-relaxed text-lg">
                  Learn DevOps, Docker, and Kubernetes by doing. We spin up instant Firecracker micro-VMs in your browser, giving you root terminal access to a live environment where you can safely break and fix infrastructure.
                </p>
                <div className="pt-4">
                  <Link href="/labs">
                    <Button variant="outline" className="group">
                      Open Cloud Labs <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </Link>
                </div>
              </TabsContent>
              
              <TabsContent value="system" className="space-y-4 m-0">
                <h3 className="text-2xl font-bold">Interactive Architecture Canvas</h3>
                <p className="text-muted-foreground leading-relaxed text-lg">
                  Master system design interviews by dragging and dropping Load Balancers, Databases, and Caches. Run traffic simulations to see where your bottlenecks are and receive live AI grading on your architecture choices.
                </p>
                <div className="pt-4">
                  <Link href="/system-design">
                    <Button variant="outline" className="group">
                      Design a System <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </Link>
                </div>
              </TabsContent>
            </div>
          </Tabs>
        </div>
        
        {/* CTA */}
        <div className="text-center animate-in fade-in duration-1000 delay-500 bg-primary/5 border border-primary/20 rounded-3xl p-12 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">Ready to elevate your skills?</h2>
          <p className="text-muted-foreground mb-8 text-lg">Join thousands of developers mastering software engineering with AI.</p>
          <Link href="/signup">
            <Button size="lg" className="h-12 px-8 text-base font-semibold rounded-full bg-primary hover:bg-primary/90 text-primary-foreground">
              Create Free Account
            </Button>
          </Link>
        </div>
      </main>
    </div>
  );
}

function Badge({ className, variant, children }: any) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${className}`}>
      {children}
    </span>
  )
}
