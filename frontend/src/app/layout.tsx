import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "UWO Graduation Checker",
  description: "Check your progression against Western University degree modules",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
