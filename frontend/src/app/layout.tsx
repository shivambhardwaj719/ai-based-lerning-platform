import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/providers/theme-provider";
import { QueryProvider } from "@/providers/query-provider";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "NexusLearn AI — Master Engineering with AI Mentorship",
    template: "%s | NexusLearn AI",
  },
  description:
    "The next-generation AI-native technical education platform. Learn coding, system design, DevOps, AI/ML, and more with personalized AI mentorship.",
  keywords: [
    "AI learning",
    "coding platform",
    "system design",
    "DevOps",
    "machine learning",
    "programming",
    "technical education",
  ],
  authors: [{ name: "NexusLearn AI Team" }],
  openGraph: {
    type: "website",
    locale: "en_US",
    title: "NexusLearn AI",
    description: "Master Engineering with AI-Native Mentorship",
    siteName: "NexusLearn AI",
  },
  twitter: {
    card: "summary_large_image",
    title: "NexusLearn AI",
    description: "Master Engineering with AI-Native Mentorship",
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f9f9fc" },
    { media: "(prefers-color-scheme: dark)", color: "#0d0d18" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} ${jetbrainsMono.variable}`}
    >
      <body suppressHydrationWarning className="antialiased bg-background text-foreground min-h-screen flex flex-col">
        <QueryProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            enableSystem
            disableTransitionOnChange
          >
            {children}
            <Toaster richColors position="bottom-right" />
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
