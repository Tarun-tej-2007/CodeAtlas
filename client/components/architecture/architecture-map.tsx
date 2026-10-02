"use client";

import { useMemo, useCallback, useEffect } from "react";
import { 
  ReactFlow, 
  Background, 
  Controls, 
  MiniMap, 
  Node, 
  Edge, 
  useNodesState, 
  useEdgesState, 
  ReactFlowProvider,
  useReactFlow,
  MarkerType
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { ArchitectureData, ArchitectureComponent } from "@/types/architecture-ui";
import { ArchitectureComponentNode } from "./architecture-component";
import { ArchitectureLayerNode } from "./architecture-layer";

const nodeTypes = {
  architectureComponent: ArchitectureComponentNode,
  architectureLayer: ArchitectureLayerNode,
};

interface ArchitectureMapProps {
  data: ArchitectureData;
  searchQuery: string;
  selectedComponentId: string | null;
  onComponentSelect: (id: string | null) => void;
  selectedLayerId: string | null;
  onLayerSelect: (id: string | null) => void;
}

function ArchitectureMapInner({ 
  data, 
  searchQuery, 
  selectedComponentId,
  onComponentSelect,
  selectedLayerId,
  onLayerSelect
}: ArchitectureMapProps) {
  const { fitView } = useReactFlow();

  const { initialNodes, initialEdges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    // Layout configuration
    const layerWidth = 800;
    let currentY = 0;
    const layerSpacing = 100;
    const paddingX = 40;
    const paddingY = 60;
    const colCount = 4;
    const nodeWidth = 160;
    const nodeHeight = 60;
    const gapX = (layerWidth - 2 * paddingX - colCount * nodeWidth) / (colCount - 1);
    const gapY = 20;

    data.layers.forEach((layer) => {
      const rowCount = Math.ceil(layer.components.length / colCount);
      const layerHeight = paddingY + (rowCount * nodeHeight) + ((rowCount - 1) * gapY) + paddingY;

      // Add layer node
      nodes.push({
        id: layer.id,
        type: "architectureLayer",
        position: { x: 0, y: currentY },
        style: { width: layerWidth, height: layerHeight },
        data: {
          layer,
          isSelected: selectedLayerId === layer.id,
        },
        draggable: false,
        selectable: true,
      });

      // Add component nodes (as children of layer)
      layer.components.forEach((comp, index) => {
        const row = Math.floor(index / colCount);
        const col = index % colCount;
        const x = paddingX + col * (nodeWidth + gapX);
        const y = paddingY + row * (nodeHeight + gapY);

        nodes.push({
          id: comp.id,
          type: "architectureComponent",
          parentId: layer.id,
          extent: "parent",
          position: { x, y },
          data: {
            component: comp,
            isSelected: selectedComponentId === comp.id,
            isDimmed: false,
          },
          draggable: false,
          selectable: true,
        });
      });

      currentY += layerHeight + layerSpacing;
    });

    // We only show edges for boundaries, or explicit violations if selected.
    // To keep it clean, we might just draw edges for violations, or based on component dependencies.
    // If a component is selected, show its dependencies/dependents.
    
    // For now, let's create edges from violations, or boundary-level edges.
    // The prompt says: "Allowed relationships: solid/subtle lines. Violations: visually emphasized lines. External: dashed."
    // Let's add edges for the boundaries themselves between layers.
    data.boundaries.forEach((b) => {
      edges.push({
        id: b.id,
        source: b.sourceLayer,
        target: b.targetLayer,
        animated: !b.allowed,
        style: {
          stroke: b.allowed ? "#475569" : "#EF4444",
          strokeWidth: b.allowed ? 2 : 3,
          strokeDasharray: b.targetLayer === "external" ? "5,5" : "none",
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: b.allowed ? "#475569" : "#EF4444",
        }
      });
    });

    // If a component is selected, we might want to show its specific violations
    data.violations.forEach((v) => {
      edges.push({
        id: v.id,
        source: v.source,
        target: v.target,
        animated: true,
        hidden: selectedComponentId ? (selectedComponentId !== v.source && selectedComponentId !== v.target) : true, // Only show if related component is selected
        style: {
          stroke: "#EF4444",
          strokeWidth: 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: "#EF4444",
        },
        zIndex: 1000,
      });
    });

    return { initialNodes: nodes, initialEdges: edges };
  }, [data, selectedLayerId, selectedComponentId]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  // Update selection and search state
  useEffect(() => {
    setNodes(nds => nds.map(node => {
      if (node.type === "architectureLayer") {
        return {
          ...node,
          data: { ...node.data, isSelected: selectedLayerId === node.id }
        };
      }
      
      if (node.type === "architectureComponent") {
        const comp = node.data.component as ArchitectureComponent;
        let isDimmed = false;
        
        if (searchQuery && !comp.name.toLowerCase().includes(searchQuery.toLowerCase())) {
          isDimmed = true;
        } else if (selectedLayerId && comp.layerId !== selectedLayerId) {
          isDimmed = true;
        }

        return {
          ...node,
          data: { 
            ...node.data, 
            isSelected: selectedComponentId === node.id,
            isDimmed 
          }
        };
      }
      return node;
    }));
  }, [selectedLayerId, selectedComponentId, searchQuery, setNodes]);

  // Initial fit view
  useEffect(() => {
    setTimeout(() => {
      fitView({ padding: 0.1, duration: 800 });
    }, 50);
  }, [fitView]);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    if (node.type === "architectureLayer") {
      onLayerSelect(node.id === selectedLayerId ? null : node.id);
      onComponentSelect(null);
    } else if (node.type === "architectureComponent") {
      onComponentSelect(node.id === selectedComponentId ? null : node.id);
      onLayerSelect(null);
    }
  }, [selectedLayerId, selectedComponentId, onLayerSelect, onComponentSelect]);

  const onPaneClick = useCallback(() => {
    onLayerSelect(null);
    onComponentSelect(null);
  }, [onLayerSelect, onComponentSelect]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      onPaneClick={onPaneClick}
      nodeTypes={nodeTypes}
      fitView
      className="bg-[#080D18]"
      minZoom={0.1}
      maxZoom={1.5}
    >
      <Background color="#1E293B" gap={20} size={1} />
      <Controls className="bg-[#0F1726] border-[#1E293B] fill-[#94A3B8]" />
      <MiniMap 
        nodeColor={(n) => {
          if (n.type === "architectureLayer") return "#0F1726";
          
          if (n.type === "architectureComponent") {
            const comp = n.data?.component as ArchitectureComponent | undefined;
            if (comp?.layerId === "presentation") return "#3B82F6";
            if (comp?.layerId === "application") return "#8B5CF6";
            if (comp?.layerId === "domain") return "#10B981";
            if (comp?.layerId === "infrastructure") return "#F59E0B";
            if (comp?.layerId === "external") return "#64748B";
          }
          return "#3B82F6";
        }}
        maskColor="rgba(8, 13, 24, 0.7)"
        className="bg-[#0B1220] border border-[#1E293B] rounded-lg shadow-sm"
      />
    </ReactFlow>
  );
}

export function ArchitectureMap(props: ArchitectureMapProps) {
  return (
    <ReactFlowProvider>
      <div className="w-full h-full relative" data-testid="architecture-map">
        <ArchitectureMapInner {...props} />
      </div>
    </ReactFlowProvider>
  );
}
