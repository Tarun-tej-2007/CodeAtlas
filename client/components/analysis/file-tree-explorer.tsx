"use client";

import { useState } from "react";
import { FileNode } from "@/types/analysis-ui";
import { ChevronRight, ChevronDown, Folder, FileCode, File, Search } from "lucide-react";

interface FileTreeExplorerProps {
  tree: FileNode[];
  onFileSelect: (file: FileNode) => void;
  selectedFileId: string | null;
}

export function FileTreeExplorer({ tree, onFileSelect, selectedFileId }: FileTreeExplorerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(["src", "src/services", "src/api/projects"]));
  const [searchQuery, setSearchQuery] = useState("");

  const toggleFolder = (folderId: string) => {
    const newSet = new Set(expandedFolders);
    if (newSet.has(folderId)) {
      newSet.delete(folderId);
    } else {
      newSet.add(folderId);
    }
    setExpandedFolders(newSet);
  };

  const renderNode = (node: FileNode, depth: number = 0) => {
    const isExpanded = expandedFolders.has(node.id);
    const isSelected = selectedFileId === node.id;
    const isFolder = node.type === "directory";

    // Basic search filtering (only filters files, hides empty folders is complex without building a new tree, so we just grey out non-matches for simplicity or hide them)
    if (searchQuery && !node.name.toLowerCase().includes(searchQuery.toLowerCase()) && !isFolder) {
      return null;
    }

    return (
      <div key={node.id} className="flex flex-col">
        <div
          className={`flex items-center py-1.5 px-2 hover:bg-[#1E293B]/50 cursor-pointer rounded-sm group ${isSelected ? 'bg-[#1E293B] text-[#3B82F6]' : 'text-[#CBD5E1]'}`}
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
          onClick={() => {
            if (isFolder) {
              toggleFolder(node.id);
            } else {
              onFileSelect(node);
            }
          }}
        >
          <div className="flex items-center gap-1.5 flex-1 min-w-0">
            {isFolder ? (
              isExpanded ? <ChevronDown className="h-3.5 w-3.5 text-[#64748B] shrink-0" /> : <ChevronRight className="h-3.5 w-3.5 text-[#64748B] shrink-0" />
            ) : (
              <div className="h-3.5 w-3.5 shrink-0" /> // spacer
            )}
            
            {isFolder ? (
              <Folder className="h-3.5 w-3.5 text-[#94A3B8] shrink-0 group-hover:text-[#CBD5E1]" />
            ) : node.language === "typescript" || node.language === "tsx" ? (
              <FileCode className={`h-3.5 w-3.5 shrink-0 ${isSelected ? 'text-[#3B82F6]' : 'text-[#3B82F6]/70 group-hover:text-[#3B82F6]'}`} />
            ) : (
              <File className="h-3.5 w-3.5 text-[#94A3B8] shrink-0" />
            )}
            
            <span className={`text-[13px] truncate ${isFolder ? 'font-medium' : ''} ${isSelected ? 'font-medium' : ''}`}>
              {node.name}
            </span>
          </div>

          {node.issueCount && node.issueCount > 0 && (
            <div className="flex items-center justify-center h-4 w-4 rounded-full bg-[#EF4444]/10 text-[#EF4444] text-[10px] font-medium ml-2 shrink-0 border border-[#EF4444]/20">
              {node.issueCount}
            </div>
          )}
        </div>
        
        {isFolder && isExpanded && node.children && (
          <div className="flex flex-col">
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-[#080D18] border border-[#1E293B] rounded-lg shadow-xs overflow-hidden">
      <div className="p-3 border-b border-[#1E293B] bg-[#0F1726]">
        <div className="relative">
          <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-[#64748B]" />
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#141E2E] border border-[#1E293B] rounded-md py-1.5 pl-8 pr-3 text-xs text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none focus:ring-1 focus:ring-[#3B82F6]"
          />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-1.5 py-2 select-none custom-scrollbar">
        {tree.map(node => renderNode(node, 0))}
      </div>
    </div>
  );
}
