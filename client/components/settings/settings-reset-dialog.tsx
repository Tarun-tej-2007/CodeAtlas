import { X, AlertTriangle } from "lucide-react";
import { useEffect } from "react";

interface ResetDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export function SettingsResetDialog({ isOpen, onClose, onConfirm }: ResetDialogProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 z-50 bg-[#080D18]/80 backdrop-blur-sm flex items-center justify-center p-4"
        onClick={onClose}
      />
      
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md bg-[#0B1220] border border-[#1E293B] shadow-2xl rounded-xl overflow-hidden">
        <div className="flex items-center justify-between p-5 border-b border-[#1E293B]">
          <h2 className="text-lg font-bold text-[#F8FAFC]">Reset Settings</h2>
          <button 
            onClick={onClose}
            className="p-1.5 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded-md transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        
        <div className="p-6">
          <div className="flex items-start gap-4 mb-6">
            <div className="p-3 bg-[#EF4444]/10 rounded-full shrink-0">
              <AlertTriangle className="h-6 w-6 text-[#EF4444]" />
            </div>
            <div>
              <p className="text-sm text-[#CBD5E1] leading-relaxed">
                Are you sure you want to reset all configurations to their deterministic default settings?
                This action will restore all default values and discard any unsaved changes.
              </p>
            </div>
          </div>
          
          <div className="flex justify-end gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] rounded-md text-sm font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                onConfirm();
                onClose();
              }}
              className="px-4 py-2 bg-[#EF4444] hover:bg-[#DC2626] text-white rounded-md text-sm font-medium transition-colors shadow"
            >
              Reset Defaults
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
