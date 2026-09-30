import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { AppQueryProvider } from "@/lib/query/providers";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "CodeAtlas - Architecture Intelligence Platform",
  description:
    "AI-powered software architecture intelligence and code health platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} dark h-full overflow-hidden antialiased`}
    >
      <body className="h-full overflow-hidden flex flex-col bg-[#080D18] text-[#F8FAFC]">
        <AppQueryProvider>{children}</AppQueryProvider>
      </body>
    </html>
  );
}
