import { SettingsSection } from "@/types/settings-ui";
import { 
  Briefcase, Activity, Hexagon, Brain, 
  ShieldCheck, Bell, Palette, Code2 
} from "lucide-react";

interface SettingsNavigationProps {
  activeSection: SettingsSection;
  onSelect: (section: SettingsSection) => void;
}

const SECTIONS: { id: SettingsSection; icon: React.ElementType }[] = [
  { id: "General", icon: Briefcase },
  { id: "Analysis", icon: Activity },
  { id: "Architecture", icon: Hexagon },
  { id: "AI", icon: Brain },
  { id: "Governance", icon: ShieldCheck },
  { id: "Notifications", icon: Bell },
  { id: "Appearance", icon: Palette },
  { id: "Developer", icon: Code2 },
];

export function SettingsNavigation({ activeSection, onSelect }: SettingsNavigationProps) {
  return (
    <nav className="flex flex-row md:flex-col gap-1 overflow-x-auto pb-2 md:pb-0 hide-scrollbar">
      {SECTIONS.map((section) => {
        const Icon = section.icon;
        const isActive = activeSection === section.id;
        
        return (
          <button
            key={section.id}
            onClick={() => onSelect(section.id)}
            className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap ${
              isActive 
                ? "bg-[#3B82F6]/10 text-[#3B82F6] border border-[#3B82F6]/20" 
                : "text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#141E2E] border border-transparent"
            }`}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {section.id}
          </button>
        );
      })}
    </nav>
  );
}
