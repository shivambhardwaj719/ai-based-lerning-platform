"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef, useState } from "react";
import { CheckCircle2, Zap, Crown, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import Link from "next/link";

const plans = [
  {
    name: "Free",
    icon: Zap,
    price: { monthly: 0, annual: 0 },
    description: "Perfect to get started and explore the platform.",
    color: "border-border/60",
    features: [
      "50 coding problems",
      "Basic study material",
      "3 AI mentor messages/day",
      "1 DevOps lab/month",
      "Community access",
    ],
    cta: "Start Free",
    ctaVariant: "outline" as const,
    href: "/signup",
  },
  {
    name: "Pro",
    icon: Rocket,
    price: { monthly: 799, annual: 599 },
    description: "For serious learners who want to accelerate their career.",
    color: "border-primary/40",
    popular: true,
    features: [
      "Unlimited coding problems",
      "All study material + AI notes",
      "Unlimited AI mentor messages",
      "All DevOps & cloud labs",
      "System design canvas",
      "AI/ML playground",
      "Contest participation",
      "Progress analytics",
      "Certificate of completion",
    ],
    cta: "Start Pro",
    ctaVariant: "default" as const,
    href: "/signup?plan=pro",
  },
  {
    name: "Team",
    icon: Crown,
    price: { monthly: 1999, annual: 1499 },
    description: "For teams and organizations training engineers at scale.",
    color: "border-amber-500/40",
    features: [
      "Everything in Pro",
      "Up to 20 seats",
      "Admin dashboard",
      "Custom roadmaps",
      "Team analytics",
      "Priority support",
      "Custom content uploads",
      "API access",
    ],
    cta: "Contact Sales",
    ctaVariant: "outline" as const,
    href: "/contact",
  },
];

export function PricingSection() {
  const [annual, setAnnual] = useState(true);
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
          <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-3">
            Simple, honest <span className="gradient-text">pricing</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-xl mx-auto mb-6">
            No hidden fees. Cancel anytime. Start free.
          </p>

          {/* Toggle */}
          <div className="inline-flex items-center gap-3 rounded-xl bg-muted/60 border border-border/40 p-1">
            <button
              onClick={() => setAnnual(false)}
              className={cn(
                "px-4 py-1.5 rounded-lg text-sm font-medium transition-colors",
                !annual ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"
              )}
            >
              Monthly
            </button>
            <button
              onClick={() => setAnnual(true)}
              className={cn(
                "flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-medium transition-colors",
                annual ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"
              )}
            >
              Annual
              <Badge className="text-[10px] bg-emerald-500/10 text-emerald-500 border-emerald-500/20">Save 25%</Badge>
            </button>
          </div>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.1 }}
              className={cn(
                "relative rounded-2xl border bg-card/60 p-7 flex flex-col",
                plan.color,
                plan.popular && "shadow-lg shadow-primary/10"
              )}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-primary text-primary-foreground px-3 text-xs">Most Popular</Badge>
                </div>
              )}

              <div className="flex items-center gap-3 mb-4">
                <div className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-xl",
                  plan.popular ? "bg-primary/10 border border-primary/20" : "bg-muted border border-border/40"
                )}>
                  <plan.icon className={cn("h-5 w-5", plan.popular ? "text-primary" : "text-muted-foreground")} />
                </div>
                <div>
                  <h3 className="font-bold text-lg">{plan.name}</h3>
                  <p className="text-xs text-muted-foreground">{plan.description}</p>
                </div>
              </div>

              <div className="mb-6">
                <div className="flex items-baseline gap-1">
                  <span className="text-xs text-muted-foreground">₹</span>
                  <span className="text-4xl font-extrabold">
                    {annual ? plan.price.annual : plan.price.monthly}
                  </span>
                  {plan.price.monthly > 0 && (
                    <span className="text-sm text-muted-foreground">/mo</span>
                  )}
                </div>
                {annual && plan.price.monthly > 0 && (
                  <p className="text-xs text-muted-foreground mt-0.5">Billed annually</p>
                )}
              </div>

              <ul className="space-y-2.5 mb-8 flex-1">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>

              <Link href={plan.href}>
                <Button
                  variant={plan.ctaVariant}
                  className={cn(
                    "w-full h-11 rounded-xl font-semibold",
                    plan.popular && "bg-primary hover:bg-primary/90"
                  )}
                >
                  {plan.cta}
                </Button>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
