"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Users, Mic, Calendar, TrendingUp } from "lucide-react";
import { crmAPI } from "@/lib/api";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    crmAPI
      .getDashboardStats()
      .then(({ data }) => setStats(data))
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return <div className="p-8">Loading dashboard...</div>;
  }

  const statCards = [
    {
      title: "Total Leads",
      value: stats?.total_leads || 0,
      subtext: `+${stats?.leads_today || 0} today`,
      icon: Users,
      color: "var(--primary)",
    },
    {
      title: "Active Conversations",
      value: stats?.active_conversations || 0,
      subtext: `${stats?.conversations_today || 0} total today`,
      icon: Mic,
      color: "var(--secondary)",
    },
    {
      title: "Appointments Booked",
      value: stats?.appointments_booked || 0,
      subtext: `+${stats?.appointments_today || 0} today`,
      icon: Calendar,
      color: "var(--accent)",
    },
    {
      title: "Avg Lead Score",
      value: stats?.avg_lead_score || 0,
      subtext: "out of 100",
      icon: TrendingUp,
      color: "var(--success)",
    },
  ];

  // Mock data for charts
  const activityData = [
    { name: "Mon", calls: 12 },
    { name: "Tue", calls: 19 },
    { name: "Wed", calls: 15 },
    { name: "Thu", calls: 22 },
    { name: "Fri", calls: 28 },
    { name: "Sat", calls: 10 },
    { name: "Sun", calls: 5 },
  ];

  const languageData = Object.entries(stats?.language_distribution || {}).map(
    ([name, value]) => ({ name, value })
  );

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold font-[family-name:var(--font-outfit)]">
          Dashboard
        </h1>
        <p className="text-[hsl(var(--muted-foreground))]">
          Overview of your AI sales performance.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[hsl(var(--muted-foreground))] text-sm font-medium">
                    {stat.title}
                  </p>
                  <h3 className="text-3xl font-bold mt-2">{stat.value}</h3>
                  <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
                    {stat.subtext}
                  </p>
                </div>
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: `hsl(${stat.color}/0.1)` }}
                >
                  <Icon
                    className="w-5 h-5"
                    style={{ color: `hsl(${stat.color})` }}
                  />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass rounded-2xl p-6 lg:col-span-2"
        >
          <h3 className="text-lg font-semibold mb-6">Call Activity (Weekly)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData}>
                <defs>
                  <linearGradient id="colorCalls" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" tick={{ fill: "hsl(var(--muted-foreground))" }} axisLine={false} tickLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" tick={{ fill: "hsl(var(--muted-foreground))" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "hsl(var(--card))", borderColor: "hsl(var(--border))", borderRadius: "8px" }}
                  itemStyle={{ color: "hsl(var(--foreground))" }}
                />
                <Area type="monotone" dataKey="calls" stroke="hsl(var(--primary))" strokeWidth={3} fillOpacity={1} fill="url(#colorCalls)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass rounded-2xl p-6"
        >
          <h3 className="text-lg font-semibold mb-6">Language Distribution</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={languageData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
                <XAxis type="number" stroke="hsl(var(--muted-foreground))" axisLine={false} tickLine={false} />
                <YAxis dataKey="name" type="category" stroke="hsl(var(--muted-foreground))" axisLine={false} tickLine={false} width={80} />
                <Tooltip
                  cursor={{ fill: "hsl(var(--muted)/0.5)" }}
                  contentStyle={{ backgroundColor: "hsl(var(--card))", borderColor: "hsl(var(--border))", borderRadius: "8px" }}
                />
                <Bar dataKey="value" fill="hsl(var(--secondary))" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
