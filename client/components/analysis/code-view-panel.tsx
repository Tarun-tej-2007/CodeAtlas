"use client";

import { useEffect, useRef } from "react";
import { FileCode, AlertCircle } from "lucide-react";

interface CodeViewPanelProps {
  filePath: string;
  code: string;
  highlightLine?: number;
  language?: string;
}

export function CodeViewPanel({ filePath, code, highlightLine, language = "typescript" }: CodeViewPanelProps) {
  const lineRefs = useRef<Record<number, HTMLDivElement | null>>({});
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (highlightLine && lineRefs.current[highlightLine] && containerRef.current) {
      const lineElement = lineRefs.current[highlightLine];
      const container = containerRef.current;
      
      // Calculate position to center the line
      const offsetTop = lineElement?.offsetTop || 0;
      const containerHeight = container.clientHeight;
      
      if (container.scrollTo) {
        container.scrollTo({
          top: Math.max(0, offsetTop - containerHeight / 2),
          behavior: "smooth"
        });
      } else {
        container.scrollTop = Math.max(0, offsetTop - containerHeight / 2);
      }
    }
  }, [highlightLine, filePath]);

  if (!code) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-[#0F1726] text-[#64748B]">
        <FileCode className="h-12 w-12 mb-4 opacity-50" />
        <p className="text-sm font-medium">Select a file to view source code</p>
      </div>
    );
  }

  const lines = code.split("\n");

  return (
    <div className="flex flex-col h-full bg-[#0F1726]">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[#1E293B] bg-[#141E2E] shadow-sm shrink-0">
        <div className="flex items-center gap-2">
          <FileCode className="h-4 w-4 text-[#3B82F6]" />
          <span className="text-sm font-mono text-[#CBD5E1] font-medium">{filePath}</span>
        </div>
        <span className="text-[10px] font-semibold uppercase tracking-wider text-[#64748B] bg-[#080D18] px-2 py-1 rounded border border-[#1E293B]">
          {language}
        </span>
      </div>

      <div 
        ref={containerRef}
        className="flex-1 overflow-auto bg-[#080D18] p-4 text-[13px] font-mono leading-relaxed"
      >
        <div className="table w-full">
          {lines.map((line, index) => {
            const lineNumber = index + 1;
            const isHighlighted = lineNumber === highlightLine;
            
            return (
              <div 
                key={lineNumber} 
                ref={el => { lineRefs.current[lineNumber] = el; }}
                className={`table-row hover:bg-[#1E293B]/30 ${isHighlighted ? 'bg-[#EF4444]/10 hover:bg-[#EF4444]/20' : ''}`}
              >
                <div className="table-cell text-right pr-4 py-0.5 select-none text-[#475569] w-12 border-r border-[#1E293B]">
                  {lineNumber}
                </div>
                <div className="table-cell pl-4 py-0.5 whitespace-pre relative">
                  {isHighlighted && (
                    <div className="absolute left-1 top-1 text-[#EF4444]">
                      <AlertCircle className="h-3.5 w-3.5" />
                    </div>
                  )}
                  {/* Basic syntax coloring simulation for standard keywords just to look realistic */}
                  <span 
                    className={`${isHighlighted ? 'text-[#F8FAFC]' : 'text-[#CBD5E1]'}`}
                    dangerouslySetInnerHTML={{
                      __html: line
                        .replace(/(import|export|class|const|let|var|function|async|await|return|if|else|try|catch|new)\b/g, '<span class="text-[#3B82F6]">$1</span>')
                        .replace(/(string|number|boolean|Promise|any|void)\b/g, '<span class="text-[#EAB308]">$1</span>')
                        .replace(/(['"].*?['"])/g, '<span class="text-[#22C55E]">$1</span>')
                        .replace(/(\/\/.*)/g, '<span class="text-[#64748B] italic">$1</span>')
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
