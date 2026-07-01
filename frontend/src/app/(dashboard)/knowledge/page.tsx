"use client";

import { useEffect, useState, useRef } from "react";
import { format } from "date-fns";
import { Upload, FileText, Trash2, Search, Loader2 } from "lucide-react";
import { knowledgeAPI } from "@/lib/api";

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocs = async () => {
    try {
      const { data } = await knowledgeAPI.getDocuments();
      setDocuments(data);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      await knowledgeAPI.upload(file);
      await fetchDocs();
    } catch (error) {
      console.error("Upload failed", error);
      alert("Failed to upload document");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return;
    try {
      await knowledgeAPI.deleteDocument(id);
      setDocuments((docs) => docs.filter((d) => d.id !== id));
    } catch (error) {
      console.error("Delete failed", error);
    }
  };

  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-[family-name:var(--font-outfit)]">
            Knowledge Base
          </h1>
          <p className="text-[hsl(var(--muted-foreground))]">
            Upload documents to train your AI sales agent.
          </p>
        </div>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept=".pdf,.docx,.csv,.txt,.md"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[hsl(var(--primary))] text-white font-semibold hover:bg-[hsl(var(--primary)/0.9)] transition-colors disabled:opacity-50"
        >
          {isUploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
          {isUploading ? "Uploading..." : "Upload Document"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="col-span-full py-12 text-center text-[hsl(var(--muted-foreground))]">
            Loading documents...
          </div>
        ) : documents.length === 0 ? (
          <div className="col-span-full glass rounded-2xl p-12 text-center border-dashed">
            <div className="w-16 h-16 rounded-full bg-[hsl(var(--muted))] flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-[hsl(var(--muted-foreground))]" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No documents yet</h3>
            <p className="text-[hsl(var(--muted-foreground))] max-w-md mx-auto">
              Upload PDFs, Word docs, or text files to teach your AI agent about your products, pricing, and FAQs.
            </p>
          </div>
        ) : (
          documents.map((doc) => (
            <div key={doc.id} className="glass rounded-2xl p-6 relative group">
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[hsl(var(--primary)/0.2)] to-[hsl(var(--secondary)/0.2)] border border-[hsl(var(--primary)/0.3)] flex items-center justify-center text-[hsl(var(--primary))]">
                  <FileText className="w-6 h-6" />
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-2 rounded-lg text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--destructive)/0.1)] hover:text-[hsl(var(--destructive))] transition-colors opacity-0 group-hover:opacity-100"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <h3 className="font-semibold text-lg truncate mb-1" title={doc.filename}>
                {doc.filename}
              </h3>
              <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
                <span className="uppercase">{doc.file_type}</span>
                <span>•</span>
                <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
              </div>
              <div className="mt-6 pt-4 border-t border-[hsl(var(--border))] flex items-center justify-between text-sm">
                <span
                  className={`px-2.5 py-1 rounded-md border font-medium ${
                    doc.processing_status === "completed"
                      ? "bg-[hsl(var(--success)/0.1)] text-[hsl(var(--success))] border-[hsl(var(--success)/0.2)]"
                      : doc.processing_status === "failed"
                      ? "bg-[hsl(var(--destructive)/0.1)] text-[hsl(var(--destructive))] border-[hsl(var(--destructive)/0.2)]"
                      : "bg-[hsl(var(--warning)/0.1)] text-[hsl(var(--warning))] border-[hsl(var(--warning)/0.2)]"
                  }`}
                >
                  {doc.processing_status.charAt(0).toUpperCase() + doc.processing_status.slice(1)}
                </span>
                <span className="text-[hsl(var(--muted-foreground))]">
                  {doc.chunk_count} chunks
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
