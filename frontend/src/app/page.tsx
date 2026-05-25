import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { HeroSection } from "@/components/landing/hero";
import { StatsSection } from "@/components/landing/stats";
import { FeaturesSection } from "@/components/landing/features";
import { TechStackSection } from "@/components/landing/tech-stack";
import { RoadmapPreview } from "@/components/landing/roadmap-preview";
import { AIMentorPreview } from "@/components/landing/ai-mentor-preview";
import { TestimonialsSection } from "@/components/landing/testimonials";
import { PricingSection } from "@/components/landing/pricing";
import { CTASection } from "@/components/landing/cta";

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1">
        <HeroSection />
        <StatsSection />
        <FeaturesSection />
        <TechStackSection />
        <RoadmapPreview />
        <AIMentorPreview />
        <TestimonialsSection />
        <PricingSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}
