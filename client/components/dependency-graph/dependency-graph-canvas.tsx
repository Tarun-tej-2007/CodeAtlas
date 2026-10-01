"use client";

import { useMemo, useCallback, useState, useEffect } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  MarkerType,
  ConnectionMode,
  useReactFlow,
  ReactFlowProvider,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { DependencyGraphData, DependencyNode } from "@/types/dependency-graph-ui";
import { DependencyGraphNode } from "./dependency-node";

interface DependencyGraphCanvasProps {
  data: DependencyGraphData;
  layout: "hierarchical" | "force" | "circular";
  selectedNodeId: string | null;
  onNodeSelect: (nodeId: string | null) => void;
  searchQuery: string;
}

const nodeTypes = {
  custom: DependencyGraphNode,
};

function GraphInner({ data, layout, selectedNodeId, onNodeSelect, searchQuery }: DependencyGraphCanvasProps) {
  const { fitView, zoomIn, zoomOut } = useReactFlow();

  // Simple deterministic layout algorithm for the mock data
  // Since we don't want heavy dependencies like dagre, we'll manually position them by layer.
  const initialNodes = useMemo(() => {
    const layers = ["presentation", "application", "domain", "infrastructure", "external"];
    
    // Group nodes by layer
    const nodesByLayer: Record<string, typeof data.nodes> = {};
    layers.forEach(l => nodesByLayer[l] = []);
    data.nodes.forEach(n => {
      if (nodesByLayer[n.layer]) nodesByLayer[n.layer].push(n);
      else nodesByLayer["external"].push(n); // fallback
    });

    return data.nodes.map((node) => {
      const layerIndex = layers.indexOf(node.layer);
      const nodesInLayer = nodesByLayer[node.layer];
      const indexInLayer = nodesInLayer.findIndex(n => n.id === node.id);
      
      let x = 0, y = 0;
      
      if (layout === "hierarchical") {
        // Vertical layout (layers top to bottom)
        const spacingX = 250;
        const spacingY = 250;
        const totalWidth = nodesInLayer.length * spacingX;
        x = indexInLayer * spacingX - (totalWidth / 2);
        y = layerIndex * spacingY;
      } else if (layout === "circular") {
        const radius = Math.max(450, data.nodes.length * 15);
        const angle = (indexInLayer / nodesInLayer.length) * 2 * Math.PI;
        x = Math.cos(angle) * radius * (layerIndex * 0.4 + 0.8);
        y = Math.sin(angle) * radius * (layerIndex * 0.4 + 0.8);
      } else {
        // Force-like (just scattered deterministically)
        x = (indexInLayer * 200) % 800 - 400 + (layerIndex * 60);
        y = (indexInLayer * 150) % 600 - 300 + (layerIndex * 100);
      }

      return {
        id: node.id,
        type: "custom",
        position: { x, y },
        data: {
          ...node,
          isSelected: false,
          isHighlighted: false,
          isDimmed: false,
        },
      } as Node;
    });
  }, [data.nodes, layout, data]);

  const initialEdges = useMemo(() => {
    return data.edges.map(edge => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: "smoothstep",
      animated: edge.isCircular,
      style: { stroke: edge.isCircular ? "#EF4444" : "#475569", strokeWidth: edge.isCircular ? 2 : 1.5 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: edge.isCircular ? "#EF4444" : "#475569",
      },
    })) as Edge[];
  }, [data.edges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Handle selection, highlighting, dimming, and search
  useEffect(() => {
    const relatedNodeIds = new Set<string>();
    
    if (selectedNodeId) {
      relatedNodeIds.add(selectedNodeId);
      data.edges.forEach(e => {
        if (e.source === selectedNodeId) relatedNodeIds.add(e.target);
        if (e.target === selectedNodeId) relatedNodeIds.add(e.source);
      });
    }

    setNodes(nds => nds.map(node => {
      const isSelected = node.id === selectedNodeId;
      const isHighlighted = relatedNodeIds.has(node.id) && !isSelected;
      let isDimmed = selectedNodeId ? !relatedNodeIds.has(node.id) : false;
      
      const label = (node.data as unknown as { label: string }).label;
      if (searchQuery && !label.toLowerCase().includes(searchQuery.toLowerCase())) {
        isDimmed = true;
      }

      return {
        ...node,
        data: {
          ...node.data,
          isSelected,
          isHighlighted,
          isDimmed
        }
      };
    }));

    setEdges(eds => eds.map(edge => {
      const isRelated = selectedNodeId 
        ? (edge.source === selectedNodeId || edge.target === selectedNodeId)
        : true;
      
      const isDimmed = selectedNodeId ? !isRelated : false;

      return {
        ...edge,
        style: {
          ...edge.style,
          stroke: isRelated ? (edge.animated ? "#EF4444" : "#94A3B8") : "#1E293B",
          opacity: isDimmed ? 0.2 : 1,
          strokeWidth: isRelated ? (edge.animated ? 2 : 2) : 1,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: isRelated ? (edge.animated ? "#EF4444" : "#94A3B8") : "#1E293B",
        }
      };
    }));
  }, [selectedNodeId, data.edges, searchQuery, setNodes, setEdges]);

  // Handle layout changes (reset positions)
  useEffect(() => {
    setNodes(initialNodes);
    setTimeout(() => {
      fitView({ padding: 0.2, duration: 800 });
    }, 50);
  }, [initialNodes, setNodes, fitView]);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    onNodeSelect(node.id === selectedNodeId ? null : node.id);
  }, [onNodeSelect, selectedNodeId]);

  const onPaneClick = useCallback(() => {
    onNodeSelect(null);
  }, [onNodeSelect]);

  useEffect(() => {
    const handleZoomIn = () => zoomIn();
    const handleZoomOut = () => zoomOut();
    const handleFitView = () => fitView({ padding: 0.2, duration: 800 });
    const handleReset = () => {
      setNodes(initialNodes);
      setTimeout(() => fitView({ padding: 0.2, duration: 800 }), 50);
    };

    document.addEventListener("xyflow-zoom-in", handleZoomIn);
    document.addEventListener("xyflow-zoom-out", handleZoomOut);
    document.addEventListener("xyflow-fit-view", handleFitView);
    document.addEventListener("xyflow-reset", handleReset);

    return () => {
      document.removeEventListener("xyflow-zoom-in", handleZoomIn);
      document.removeEventListener("xyflow-zoom-out", handleZoomOut);
      document.removeEventListener("xyflow-fit-view", handleFitView);
      document.removeEventListener("xyflow-reset", handleReset);
    };
  }, [zoomIn, zoomOut, fitView, initialNodes, setNodes]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      onPaneClick={onPaneClick}
      nodeTypes={nodeTypes}
      connectionMode={ConnectionMode.Loose}
      fitView
      minZoom={0.1}
      maxZoom={4}
      proOptions={{ hideAttribution: true }} // standard XYFlow practice if licensed/dev
    >
      <Background color="#1E293B" gap={20} size={1} />
      <MiniMap 
        nodeColor={(n) => {
          if (n.data?.layer === "external") return "#64748B";
          if (n.data?.layer === "application") return "#8B5CF6";
          return "#3B82F6";
        }}
        maskColor="rgba(8, 13, 24, 0.7)"
        className="bg-[#0F1726] border border-[#1E293B] !rounded-md overflow-hidden hidden sm:block" 
      />
      {/* We hide default controls because we build custom toolbar ones */}
      <Controls showInteractive={false} className="hidden" />
    </ReactFlow>
  );
}

export function DependencyGraphCanvas(props: DependencyGraphCanvasProps) {
  return (
    <ReactFlowProvider>
      <GraphInner {...props} />
    </ReactFlowProvider>
  );
}
