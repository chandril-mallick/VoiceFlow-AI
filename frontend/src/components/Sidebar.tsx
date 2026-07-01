"use client";

import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Users,
  Database,
  Mic,
  Settings,
  LogOut,
} from "lucide-react";
import { useAuth } from "@/lib/auth";

export function Sidebar() {
  const pathname = usePathname();
  const { logout, tenant } = useAuth();

  const links = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Leads", href: "/leads", icon: Users },
    { name: "Knowledge Base", href: "/knowledge", icon: Database },
    { name: "Voice Agent", href: "/voice", icon: Mic },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <div className="w-64 h-screen border-r border-[hsl(var(--border))] bg-[hsl(var(--card))] flex flex-col">
      <div className="h-16 flex items-center px-6 border-b border-[hsl(var(--border))]">
        <Mic className="w-6 h-6 text-[hsl(var(--primary))] mr-3" />
        <span className="font-bold text-lg font-[family-name:var(--font-outfit)]">
          VoiceFlow AI
        </span>
      </div>

      <div className="p-4 flex-1 space-y-1">
        {links.map((link) => {
          const isActive = pathname === link.href;
          const Icon = link.icon;
          return (
            <Link key={link.name} href={link.href}>
              <div
                className={`flex items-center px-4 py-3 rounded-xl transition-all ${
                  isActive
                    ? "bg-[hsl(var(--primary)/0.1)] text-[hsl(var(--primary))] font-medium"
                    : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted)/0.5)] hover:text-[hsl(var(--foreground))]"
                }`}
              >
                <Icon className={`w-5 h-5 mr-3 ${isActive ? "text-[hsl(var(--primary))]" : ""}`} />
                {link.name}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-indicator"
                    className="absolute left-0 w-1 h-8 bg-[hsl(var(--primary))] rounded-r-full"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </div>
            </Link>
          );
        })}
      </div>

      <div className="p-4 border-t border-[hsl(var(--border))]">
        <div className="flex items-center px-4 py-3 mb-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[hsl(var(--primary))] to-[hsl(var(--secondary))] flex items-center justify-center text-white font-bold text-sm mr-3">
            {tenant?.name.charAt(0) || "T"}
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="text-sm font-medium truncate">{tenant?.name || "Loading..."}</div>
            <div className="text-xs text-[hsl(var(--muted-foreground))] truncate">
              {tenant?.subscription_plan || "Free"} Plan
            </div>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center px-4 py-3 rounded-xl text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--destructive)/0.1)] hover:text-[hsl(var(--destructive))] transition-colors"
        >
          <LogOut className="w-5 h-5 mr-3" />
          Log Out
        </button>
      </div>
    </div>
  );
}
