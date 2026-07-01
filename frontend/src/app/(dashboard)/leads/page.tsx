"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { Search, Filter, Phone, Mail, Building, Target } from "lucide-react";
import { crmAPI } from "@/lib/api";

export default function LeadsPage() {
  const [leads, setLeads] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    crmAPI
      .getLeads()
      .then(({ data }) => setLeads(data))
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "new":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      case "contacted":
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
      case "qualified":
        return "bg-green-500/10 text-green-500 border-green-500/20";
      case "unqualified":
        return "bg-red-500/10 text-red-500 border-red-500/20";
      default:
        return "bg-gray-500/10 text-gray-500 border-gray-500/20";
    }
  };

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold font-[family-name:var(--font-outfit)]">
            Leads
          </h1>
          <p className="text-[hsl(var(--muted-foreground))]">
            Manage your AI-generated leads and prospects.
          </p>
        </div>
      </div>

      <div className="glass rounded-2xl flex-1 flex flex-col overflow-hidden">
        {/* Toolbar */}
        <div className="p-4 border-b border-[hsl(var(--border))] flex items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
            <input
              type="text"
              placeholder="Search leads..."
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-[hsl(var(--muted)/0.5)] border border-[hsl(var(--border))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground)/0.5)] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary)/0.5)] text-sm"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-[hsl(var(--border))] hover:bg-[hsl(var(--muted)/0.5)] transition-colors text-sm font-medium">
            <Filter className="w-4 h-4" />
            Filter
          </button>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-[hsl(var(--muted)/0.2)] sticky top-0 backdrop-blur-md z-10">
              <tr>
                <th className="px-6 py-4 text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
                  Lead
                </th>
                <th className="px-6 py-4 text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-4 text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-4 text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
                  Date
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[hsl(var(--border))]">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-[hsl(var(--muted-foreground))]">
                    Loading leads...
                  </td>
                </tr>
              ) : leads.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-[hsl(var(--muted-foreground))]">
                    No leads found. Start a voice conversation to generate leads.
                  </td>
                </tr>
              ) : (
                leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-[hsl(var(--muted)/0.3)] transition-colors cursor-pointer group">
                    <td className="px-6 py-4">
                      <div className="font-medium text-[hsl(var(--foreground))]">{lead.name}</div>
                      <div className="text-sm text-[hsl(var(--muted-foreground))] flex items-center mt-1">
                        <Building className="w-3.5 h-3.5 mr-1" />
                        {lead.company || "Unknown Company"}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm space-y-1">
                        {lead.email && (
                          <div className="flex items-center text-[hsl(var(--muted-foreground))]">
                            <Mail className="w-3.5 h-3.5 mr-2" />
                            {lead.email}
                          </div>
                        )}
                        {lead.phone && (
                          <div className="flex items-center text-[hsl(var(--muted-foreground))]">
                            <Phone className="w-3.5 h-3.5 mr-2" />
                            {lead.phone}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Target className="w-4 h-4 text-[hsl(var(--primary))]" />
                        <span className="font-semibold">{lead.lead_score}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-3 py-1 text-xs font-medium border rounded-full inline-block ${getStatusColor(
                          lead.status
                        )}`}
                      >
                        {lead.status.replace("_", " ").toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-[hsl(var(--muted-foreground))]">
                      {format(new Date(lead.created_at), "MMM d, yyyy")}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
