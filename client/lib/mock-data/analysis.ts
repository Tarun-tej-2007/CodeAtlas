import {
  AnalysisMetrics,
  AnalysisIssue,
  FileNode,
  ComplexityDataPoint,
  AnalysisHistoryEntry
} from "@/types/analysis-ui";

export const MOCK_ANALYSIS_METRICS: AnalysisMetrics = {
  totalFiles: 347,
  linesOfCode: 48291,
  technicalDebtRatio: 6.8,
  issues: 23,
  codeSmells: 17,
  duplicatedLines: 4.2,
  testCoverage: 81,
};

export const MOCK_ANALYSIS_ISSUES: AnalysisIssue[] = [
  {
    id: "issue-1",
    severity: "CRITICAL",
    type: "Architecture",
    title: "Controller directly accesses repository",
    description: "Controllers should not access repositories directly. Use the service layer to encapsulate business logic.",
    filePath: "src/api/projects/controller.ts",
    line: 42,
    rule: "ARCH-001",
    status: "Open",
    detected: "ProjectController\n      ↓\nProjectRepository",
    expected: "ProjectController\n      ↓\nProjectService\n      ↓\nProjectRepository",
  },
  {
    id: "issue-2",
    severity: "HIGH",
    type: "Complexity",
    title: "Function complexity exceeds threshold",
    description: "The function 'analyzeRepository' has a cyclomatic complexity of 18, which exceeds the maximum allowed threshold of 15.",
    filePath: "src/services/analysis-service.ts",
    line: 87,
    rule: "COMPLEXITY-001",
    status: "Open",
  },
  {
    id: "issue-3",
    severity: "MEDIUM",
    type: "Code Smell",
    title: "Large function",
    description: "Function 'buildDependencyGraph' contains 124 lines of code. Consider refactoring into smaller, more focused functions.",
    filePath: "src/services/architecture-service.ts",
    line: 124,
    rule: "CODE-002",
    status: "Open",
  },
  {
    id: "issue-4",
    severity: "LOW",
    type: "Duplication",
    title: "Duplicated code block",
    description: "This code block is duplicated in 2 other files.",
    filePath: "src/components/dashboard/page.tsx",
    line: 15,
    rule: "DUP-001",
    status: "Open",
  },
  {
    id: "issue-5",
    severity: "CRITICAL",
    type: "Security",
    title: "Hardcoded secret",
    description: "A potential hardcoded secret or token was detected.",
    filePath: "src/infrastructure/database.ts",
    line: 12,
    rule: "SEC-004",
    status: "Open",
  }
];

export const MOCK_FILE_TREE: FileNode[] = [
  {
    id: "src",
    name: "src",
    type: "directory",
    path: "src",
    children: [
      {
        id: "src/app",
        name: "app",
        type: "directory",
        path: "src/app",
        children: [
          {
            id: "src/app/dashboard",
            name: "dashboard",
            type: "directory",
            path: "src/app/dashboard",
            children: [
              { id: "src/app/dashboard/page.tsx", name: "page.tsx", type: "file", path: "src/app/dashboard/page.tsx", language: "tsx", issueCount: 1 }
            ]
          },
          {
            id: "src/app/projects",
            name: "projects",
            type: "directory",
            path: "src/app/projects",
            children: [
              { id: "src/app/projects/page.tsx", name: "page.tsx", type: "file", path: "src/app/projects/page.tsx", language: "tsx" }
            ]
          },
          {
            id: "src/app/api",
            name: "api",
            type: "directory",
            path: "src/app/api",
            children: [
              {
                id: "src/app/api/projects",
                name: "projects",
                type: "directory",
                path: "src/app/api/projects",
                children: [
                  { id: "src/api/projects/controller.ts", name: "controller.ts", type: "file", path: "src/api/projects/controller.ts", language: "typescript", issueCount: 1 }
                ]
              }
            ]
          }
        ]
      },
      {
        id: "src/components",
        name: "components",
        type: "directory",
        path: "src/components",
        children: [
          { id: "src/components/dashboard", name: "dashboard", type: "directory", path: "src/components/dashboard" },
          { id: "src/components/projects", name: "projects", type: "directory", path: "src/components/projects" },
          { id: "src/components/layout", name: "layout", type: "directory", path: "src/components/layout" }
        ]
      },
      {
        id: "src/lib",
        name: "lib",
        type: "directory",
        path: "src/lib",
        children: [
          { id: "src/lib/api", name: "api", type: "directory", path: "src/lib/api" },
          { id: "src/lib/utils", name: "utils", type: "directory", path: "src/lib/utils" }
        ]
      },
      {
        id: "src/services",
        name: "services",
        type: "directory",
        path: "src/services",
        children: [
          { id: "src/services/project-service.ts", name: "project-service.ts", type: "file", path: "src/services/project-service.ts", language: "typescript" },
          { id: "src/services/analysis-service.ts", name: "analysis-service.ts", type: "file", path: "src/services/analysis-service.ts", language: "typescript", issueCount: 1 },
          { id: "src/services/architecture-service.ts", name: "architecture-service.ts", type: "file", path: "src/services/architecture-service.ts", language: "typescript", issueCount: 1 }
        ]
      },
      {
        id: "src/domain",
        name: "domain",
        type: "directory",
        path: "src/domain",
        children: [
          { id: "src/domain/project.ts", name: "project.ts", type: "file", path: "src/domain/project.ts", language: "typescript" },
          { id: "src/domain/analysis.ts", name: "analysis.ts", type: "file", path: "src/domain/analysis.ts", language: "typescript" }
        ]
      },
      {
        id: "src/infrastructure",
        name: "infrastructure",
        type: "directory",
        path: "src/infrastructure",
        children: [
          { id: "src/infrastructure/database.ts", name: "database.ts", type: "file", path: "src/infrastructure/database.ts", language: "typescript", issueCount: 1 },
          { id: "src/infrastructure/redis.ts", name: "redis.ts", type: "file", path: "src/infrastructure/redis.ts", language: "typescript" }
        ]
      }
    ]
  }
];

export const MOCK_COMPLEXITY_DATA: ComplexityDataPoint[] = [
  { label: "analysis-service.ts", value: 18 },
  { label: "project-service.ts", value: 12 },
  { label: "architecture-service.ts", value: 9 },
  { label: "controller.ts", value: 7 },
  { label: "database.ts", value: 5 },
  { label: "page.tsx", value: 3 },
];

export const MOCK_ANALYSIS_HISTORY: AnalysisHistoryEntry[] = [
  {
    id: "hist-1",
    timestamp: "Oct 01, 2026",
    duration: "42.8s",
    filesAnalyzed: 347,
    issuesFound: 23,
    status: "Completed"
  },
  {
    id: "hist-2",
    timestamp: "Sep 30, 2026",
    duration: "39.2s",
    filesAnalyzed: 341,
    issuesFound: 27,
    status: "Completed"
  },
  {
    id: "hist-3",
    timestamp: "Sep 28, 2026",
    duration: "41.7s",
    filesAnalyzed: 338,
    issuesFound: 29,
    status: "Completed"
  }
];

export const MOCK_FILE_CONTENTS: Record<string, string> = {
  "src/api/projects/controller.ts": `import { Request, Response } from 'express';
import { ProjectRepository } from '../../infrastructure/database';
import { ProjectService } from '../../services/project-service';

export class ProjectController {
  private projectRepository: ProjectRepository;
  private projectService: ProjectService;

  constructor() {
    this.projectRepository = new ProjectRepository();
    this.projectService = new ProjectService();
  }

  async getProjects(req: Request, res: Response) {
    try {
      const projects = await this.projectService.listProjects();
      return res.status(200).json(projects);
    } catch (error) {
      return res.status(500).json({ error: 'Failed to fetch projects' });
    }
  }

  async getProject(req: Request, res: Response) {
    const { id } = req.params;
    
    // ARCH-001: Controller directly accesses repository
    // This violates the layered architecture principle
    const project = await this.projectRepository.findById(id);
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    return res.status(200).json(project);
  }
  
  async createProject(req: Request, res: Response) {
    try {
      const project = await this.projectService.createProject(req.body);
      return res.status(201).json(project);
    } catch (error) {
      return res.status(400).json({ error: error.message });
    }
  }
}`,
  "src/services/analysis-service.ts": `import { Repository } from '../domain/project';
import { AnalysisResult } from '../domain/analysis';

export class AnalysisService {
  
  // COMPLEXITY-001: Function complexity exceeds threshold
  async analyzeRepository(repo: Repository): Promise<AnalysisResult> {
    const result = new AnalysisResult();
    
    if (!repo) {
      throw new Error("Repository is required");
    }
    
    if (repo.isArchived) {
      result.status = 'skipped';
      return result;
    }
    
    try {
      const files = await this.fetchFiles(repo);
      
      for (const file of files) {
        if (file.extension === '.ts' || file.extension === '.tsx') {
          const ast = this.parseTypescript(file);
          
          if (ast.hasErrors) {
            result.errors.push(\`Syntax error in \${file.path}\`);
            continue;
          }
          
          const complexity = this.calculateComplexity(ast);
          
          if (complexity > 15) {
            result.warnings.push(\`High complexity in \${file.path}\`);
          }
          
          const deps = this.extractDependencies(ast);
          result.dependencies.push(...deps);
          
          if (this.isController(file)) {
            const violatesArch = this.checkArchitectureRules(ast);
            if (violatesArch) {
              result.violations.push(\`Architecture violation in \${file.path}\`);
            }
          }
        } else if (file.extension === '.js') {
          // Legacy JS support
          const ast = this.parseJavascript(file);
          // ... more nested logic
        }
      }
      
      result.status = 'completed';
    } catch (error) {
      result.status = 'failed';
      result.errors.push(error.message);
    }
    
    return result;
  }
  
  // ... other methods
}
`
};
