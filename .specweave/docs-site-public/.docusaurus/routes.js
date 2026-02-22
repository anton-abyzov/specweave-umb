import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '/',
    component: ComponentCreator('/', '377'),
    routes: [
      {
        path: '/',
        component: ComponentCreator('/', 'ac9'),
        routes: [
          {
            path: '/tags',
            component: ComponentCreator('/tags', 'ce1'),
            exact: true
          },
          {
            path: '/tags/ai',
            component: ComponentCreator('/tags/ai', '144'),
            exact: true
          },
          {
            path: '/tags/ai-agents',
            component: ComponentCreator('/tags/ai-agents', 'd48'),
            exact: true
          },
          {
            path: '/tags/ai-coding',
            component: ComponentCreator('/tags/ai-coding', 'b3e'),
            exact: true
          },
          {
            path: '/tags/anthropic',
            component: ComponentCreator('/tags/anthropic', '2a3'),
            exact: true
          },
          {
            path: '/tags/claude-code',
            component: ComponentCreator('/tags/claude-code', 'f2d'),
            exact: true
          },
          {
            path: '/tags/claudecode',
            component: ComponentCreator('/tags/claudecode', 'b90'),
            exact: true
          },
          {
            path: '/tags/developer-tools',
            component: ComponentCreator('/tags/developer-tools', '31e'),
            exact: true
          },
          {
            path: '/tags/productivity',
            component: ComponentCreator('/tags/productivity', '7f3'),
            exact: true
          },
          {
            path: '/tags/prompt-injection',
            component: ComponentCreator('/tags/prompt-injection', 'b87'),
            exact: true
          },
          {
            path: '/tags/security',
            component: ComponentCreator('/tags/security', '84b'),
            exact: true
          },
          {
            path: '/tags/specweave',
            component: ComponentCreator('/tags/specweave', 'b85'),
            exact: true
          },
          {
            path: '/tags/supply-chain',
            component: ComponentCreator('/tags/supply-chain', 'fd5'),
            exact: true
          },
          {
            path: '/tags/webdev',
            component: ComponentCreator('/tags/webdev', 'a08'),
            exact: true
          },
          {
            path: '/',
            component: ComponentCreator('/', '83e'),
            routes: [
              {
                path: '/academy/',
                component: ComponentCreator('/academy/', '728'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/academy/videos/_TEMPLATE',
                component: ComponentCreator('/academy/videos/_TEMPLATE', '580'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/academy/videos/clawhub-postmortem',
                component: ComponentCreator('/academy/videos/clawhub-postmortem', '101'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/academy/videos/specweave-complete-masterclass',
                component: ComponentCreator('/academy/videos/specweave-complete-masterclass', 'fbc'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/academy/videos/stop-repeating-yourself',
                component: ComponentCreator('/academy/videos/stop-repeating-yourself', 'dbc'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/academy/videos/toxicskills-security',
                component: ComponentCreator('/academy/videos/toxicskills-security', '4bc'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/api/',
                component: ComponentCreator('/api/', 'b86'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands',
                component: ComponentCreator('/commands', '05c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/abandon',
                component: ComponentCreator('/commands/abandon', 'b36'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/auto',
                component: ComponentCreator('/commands/auto', '7fa'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/auto-status',
                component: ComponentCreator('/commands/auto-status', '79e'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/cancel-auto',
                component: ComponentCreator('/commands/cancel-auto', 'd3f'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/do',
                component: ComponentCreator('/commands/do', 'ba5'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/jobs',
                component: ComponentCreator('/commands/jobs', '7e3'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/overview',
                component: ComponentCreator('/commands/overview', 'ba9'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/pause',
                component: ComponentCreator('/commands/pause', '354'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/resume',
                component: ComponentCreator('/commands/resume', '688'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/status',
                component: ComponentCreator('/commands/status', '6e0'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/commands/status-management',
                component: ComponentCreator('/commands/status-management', 'c63'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/development',
                component: ComponentCreator('/development', 'e86'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/development/claude-cli-automation',
                component: ComponentCreator('/development/claude-cli-automation', '7cd'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/faq',
                component: ComponentCreator('/faq', 'def'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/features',
                component: ComponentCreator('/features', '43c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/',
                component: ComponentCreator('/glossary/', '5c3'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/categories/architecture-category',
                component: ComponentCreator('/glossary/categories/architecture-category', '022'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/categories/backend-category',
                component: ComponentCreator('/glossary/categories/backend-category', '1d8'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/categories/category-pages-complete',
                component: ComponentCreator('/glossary/categories/category-pages-complete', '2b1'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/categories/collaboration-category',
                component: ComponentCreator('/glossary/categories/collaboration-category', 'c6a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/categories/devops-category',
                component: ComponentCreator('/glossary/categories/devops-category', 'e30'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/categories/frontend-category',
                component: ComponentCreator('/glossary/categories/frontend-category', 'ac0'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/categories/infrastructure-category',
                component: ComponentCreator('/glossary/categories/infrastructure-category', '6e3'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/categories/ml-ai-category',
                component: ComponentCreator('/glossary/categories/ml-ai-category', '561'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/categories/performance-category',
                component: ComponentCreator('/glossary/categories/performance-category', 'd64'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/categories/testing-category',
                component: ComponentCreator('/glossary/categories/testing-category', 'e73'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/index-by-category',
                component: ComponentCreator('/glossary/index-by-category', '8e7'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/ac-id',
                component: ComponentCreator('/glossary/terms/ac-id', 'a3f'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/acceptance-criteria',
                component: ComponentCreator('/glossary/terms/acceptance-criteria', '25e'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/adr',
                component: ComponentCreator('/glossary/terms/adr', '792'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/angular',
                component: ComponentCreator('/glossary/terms/angular', '711'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/api',
                component: ComponentCreator('/glossary/terms/api', '2b0'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/bdd',
                component: ComponentCreator('/glossary/terms/bdd', 'c22'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/bidirectional-sync',
                component: ComponentCreator('/glossary/terms/bidirectional-sync', 'b5c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/brownfield',
                component: ComponentCreator('/glossary/terms/brownfield', '3d8'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/ci-cd',
                component: ComponentCreator('/glossary/terms/ci-cd', '982'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/content-classification',
                component: ComponentCreator('/glossary/terms/content-classification', '48a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/copied-acs-and-tasks',
                component: ComponentCreator('/glossary/terms/copied-acs-and-tasks', 'f1a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/cross-linking',
                component: ComponentCreator('/glossary/terms/cross-linking', 'b9b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/docker',
                component: ComponentCreator('/glossary/terms/docker', '952'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/docusaurus-frontmatter',
                component: ComponentCreator('/glossary/terms/docusaurus-frontmatter', 'e16'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/e2e',
                component: ComponentCreator('/glossary/terms/e2e', '2bb'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/fda',
                component: ComponentCreator('/glossary/terms/fda', '263'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/git',
                component: ComponentCreator('/glossary/terms/git', 'd27'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/github-actions',
                component: ComponentCreator('/glossary/terms/github-actions', 'cf1'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/graphql',
                component: ComponentCreator('/glossary/terms/graphql', '34d'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/greenfield',
                component: ComponentCreator('/glossary/terms/greenfield', 'fa2'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/hipaa',
                component: ComponentCreator('/glossary/terms/hipaa', 'ecf'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/hooks',
                component: ComponentCreator('/glossary/terms/hooks', '2ab'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/iac',
                component: ComponentCreator('/glossary/terms/iac', '9f2'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/increments',
                component: ComponentCreator('/glossary/terms/increments', '6d2'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/integration-testing',
                component: ComponentCreator('/glossary/terms/integration-testing', '76f'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/intelligent-living-docs-sync',
                component: ComponentCreator('/glossary/terms/intelligent-living-docs-sync', 'd09'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/kubernetes',
                component: ComponentCreator('/glossary/terms/kubernetes', 'ba6'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/living-docs',
                component: ComponentCreator('/glossary/terms/living-docs', 'bfc'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/microservices',
                component: ComponentCreator('/glossary/terms/microservices', '68f'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/monolith',
                component: ComponentCreator('/glossary/terms/monolith', '422'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/nextjs',
                component: ComponentCreator('/glossary/terms/nextjs', '04e'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/nodejs',
                component: ComponentCreator('/glossary/terms/nodejs', '74c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/playwright',
                component: ComponentCreator('/glossary/terms/playwright', '8a2'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/profile-based-sync',
                component: ComponentCreator('/glossary/terms/profile-based-sync', '717'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/project-detection',
                component: ComponentCreator('/glossary/terms/project-detection', '412'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/project-specific-tasks',
                component: ComponentCreator('/glossary/terms/project-specific-tasks', '788'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/react',
                component: ComponentCreator('/glossary/terms/react', '740'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/rest',
                component: ComponentCreator('/glossary/terms/rest', '982'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/rfc',
                component: ComponentCreator('/glossary/terms/rfc', '05c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/role-orchestrator',
                component: ComponentCreator('/glossary/terms/role-orchestrator', 'd10'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/skills-vs-agents',
                component: ComponentCreator('/glossary/terms/skills-vs-agents', 'c07'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/soc2',
                component: ComponentCreator('/glossary/terms/soc2', '9eb'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/source-of-truth',
                component: ComponentCreator('/glossary/terms/source-of-truth', 'a4e'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/spa',
                component: ComponentCreator('/glossary/terms/spa', 'e63'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/specs',
                component: ComponentCreator('/glossary/terms/specs', '106'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/ssg',
                component: ComponentCreator('/glossary/terms/ssg', 'b78'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/ssr',
                component: ComponentCreator('/glossary/terms/ssr', 'e6c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/strategic-init',
                component: ComponentCreator('/glossary/terms/strategic-init', '429'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/tdd',
                component: ComponentCreator('/glossary/terms/tdd', '905'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/terraform',
                component: ComponentCreator('/glossary/terms/terraform', 'eba'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/test-coverage',
                component: ComponentCreator('/glossary/terms/test-coverage', 'cc2'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/test-pyramid',
                component: ComponentCreator('/glossary/terms/test-pyramid', 'a42'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/three-layer-architecture',
                component: ComponentCreator('/glossary/terms/three-layer-architecture', '822'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/three-permission-architecture',
                component: ComponentCreator('/glossary/terms/three-permission-architecture', '591'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/typescript',
                component: ComponentCreator('/glossary/terms/typescript', '973'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/unit-testing',
                component: ComponentCreator('/glossary/terms/unit-testing', 'b2b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/user-stories',
                component: ComponentCreator('/glossary/terms/user-stories', 'e2a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/glossary/terms/wip-limits',
                component: ComponentCreator('/glossary/terms/wip-limits', 'f28'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides',
                component: ComponentCreator('/guides', 'df2'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/ado-multi-project-migration',
                component: ComponentCreator('/guides/ado-multi-project-migration', '6b6'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/autonomous-execution',
                component: ComponentCreator('/guides/autonomous-execution', '553'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/backlog-management',
                component: ComponentCreator('/guides/backlog-management', '2f9'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/best-practices',
                component: ComponentCreator('/guides/best-practices', 'b2f'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/bidirectional-linking',
                component: ComponentCreator('/guides/bidirectional-linking', 'f23'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/command-reference-by-priority',
                component: ComponentCreator('/guides/command-reference-by-priority', '556'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/compliance-standards',
                component: ComponentCreator('/guides/compliance-standards', '751'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/core-concepts/background-jobs',
                component: ComponentCreator('/guides/core-concepts/background-jobs', 'b1d'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/core-concepts/living-docs-sync-strategy',
                component: ComponentCreator('/guides/core-concepts/living-docs-sync-strategy', '580'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/core-concepts/living-documentation',
                component: ComponentCreator('/guides/core-concepts/living-documentation', 'c40'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/core-concepts/what-is-an-increment',
                component: ComponentCreator('/guides/core-concepts/what-is-an-increment', '609'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/cost-optimization',
                component: ComponentCreator('/guides/cost-optimization', 'b2a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/deep-interview-mode',
                component: ComponentCreator('/guides/deep-interview-mode', '4a9'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/getting-started/installation',
                component: ComponentCreator('/guides/getting-started/installation', 'aca'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/getting-started/nvm-global-packages-fix',
                component: ComponentCreator('/guides/getting-started/nvm-global-packages-fix', '627'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/getting-started/quickstart',
                component: ComponentCreator('/guides/getting-started/quickstart', '324'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/github-action-setup',
                component: ComponentCreator('/guides/github-action-setup', 'b5b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/github-integration',
                component: ComponentCreator('/guides/github-integration', '77a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/hierarchy-mapping',
                component: ComponentCreator('/guides/hierarchy-mapping', '32e'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/increment-status-reference',
                component: ComponentCreator('/guides/increment-status-reference', 'fd3'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/intelligent-living-docs-sync',
                component: ComponentCreator('/guides/intelligent-living-docs-sync', '6e5'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/kafka-advanced-usage',
                component: ComponentCreator('/guides/kafka-advanced-usage', '6ae'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/kafka-getting-started',
                component: ComponentCreator('/guides/kafka-getting-started', 'ce7'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/kafka-terraform',
                component: ComponentCreator('/guides/kafka-terraform', 'f0f'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/kafka-troubleshooting',
                component: ComponentCreator('/guides/kafka-troubleshooting', '449'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/meta-capability',
                component: ComponentCreator('/guides/meta-capability', '7ac'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/migration-v024',
                component: ComponentCreator('/guides/migration-v024', 'e81'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/migration-v031-project-fields',
                component: ComponentCreator('/guides/migration-v031-project-fields', '39a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/mobile/react-native-setup-guide',
                component: ComponentCreator('/guides/mobile/react-native-setup-guide', 'cf2'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/model-selection',
                component: ComponentCreator('/guides/model-selection', 'd45'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/multi-project-setup',
                component: ComponentCreator('/guides/multi-project-setup', 'be7'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/multi-project-sync-architecture',
                component: ComponentCreator('/guides/multi-project-sync-architecture', '422'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/multilingual-guide',
                component: ComponentCreator('/guides/multilingual-guide', '99c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/openclaw-agent-setup',
                component: ComponentCreator('/guides/openclaw-agent-setup', '12d'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/plugin-management',
                component: ComponentCreator('/guides/plugin-management', 'c5b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/project-specific-tasks',
                component: ComponentCreator('/guides/project-specific-tasks', 'a6e'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/repository-selection',
                component: ComponentCreator('/guides/repository-selection', '02b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/scheduling-and-planning',
                component: ComponentCreator('/guides/scheduling-and-planning', 'cc0'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/spec-bidirectional-sync',
                component: ComponentCreator('/guides/spec-bidirectional-sync', '6f9'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/spec-commit-sync',
                component: ComponentCreator('/guides/spec-commit-sync', '253'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/specs-organization-guide',
                component: ComponentCreator('/guides/specs-organization-guide', '707'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/specweave-vs-speckit',
                component: ComponentCreator('/guides/specweave-vs-speckit', '182'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/status-sync-guide',
                component: ComponentCreator('/guides/status-sync-guide', '7ed'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/status-sync-migration',
                component: ComponentCreator('/guides/status-sync-migration', '2ae'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/strategic-init',
                component: ComponentCreator('/guides/strategic-init', '80d'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/sync-configuration',
                component: ComponentCreator('/guides/sync-configuration', 'd30'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/sync-strategies',
                component: ComponentCreator('/guides/sync-strategies', '5ad'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/guides/why-verified-skill-matters',
                component: ComponentCreator('/guides/why-verified-skill-matters', '4cb'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/integrations',
                component: ComponentCreator('/integrations', '557'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/integrations/generic-ai-tools',
                component: ComponentCreator('/integrations/generic-ai-tools', 'da5'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/integrations/issue-trackers',
                component: ComponentCreator('/integrations/issue-trackers', '45b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn',
                component: ComponentCreator('/learn', 'cbf'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn/backend/backend-fundamentals',
                component: ComponentCreator('/learn/backend/backend-fundamentals', '026'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn/foundations/claude-code-basics',
                component: ComponentCreator('/learn/foundations/claude-code-basics', '72a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn/foundations/enterprise-app-development',
                component: ComponentCreator('/learn/foundations/enterprise-app-development', 'cbe'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn/foundations/software-engineering-roles',
                component: ComponentCreator('/learn/foundations/software-engineering-roles', '578'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn/foundations/terminal-empowerment',
                component: ComponentCreator('/learn/foundations/terminal-empowerment', '3a1'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn/frontend/frontend-fundamentals',
                component: ComponentCreator('/learn/frontend/frontend-fundamentals', '723'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn/infrastructure/iac-fundamentals',
                component: ComponentCreator('/learn/infrastructure/iac-fundamentals', '093'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn/ml-ai/ml-fundamentals',
                component: ComponentCreator('/learn/ml-ai/ml-fundamentals', 'f8c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn/testing/cli-integration-testing',
                component: ComponentCreator('/learn/testing/cli-integration-testing', '6d3'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/learn/testing/testing-fundamentals',
                component: ComponentCreator('/learn/testing/testing-fundamentals', '75f'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/marketing',
                component: ComponentCreator('/marketing', '6dc'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/marketing/dev-to-article-clean',
                component: ComponentCreator('/marketing/dev-to-article-clean', '2b9'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/marketing/hooks-skill-workaround-posts',
                component: ComponentCreator('/marketing/hooks-skill-workaround-posts', '5ef'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/marketing/thariq-skills-response',
                component: ComponentCreator('/marketing/thariq-skills-response', 'd2b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/marketing/toxicskills-security-posts',
                component: ComponentCreator('/marketing/toxicskills-security-posts', 'd6e'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/metrics',
                component: ComponentCreator('/metrics', 'c46'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/overview',
                component: ComponentCreator('/overview', '1c7'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/overview/features',
                component: ComponentCreator('/overview/features', '215'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/overview/introduction',
                component: ComponentCreator('/overview/introduction', '943'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/overview/philosophy',
                component: ComponentCreator('/overview/philosophy', 'f07'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/overview/plugins-ecosystem',
                component: ComponentCreator('/overview/plugins-ecosystem', '796'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/reference',
                component: ComponentCreator('/reference', '6b8'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/reference/cost-tracking',
                component: ComponentCreator('/reference/cost-tracking', '09b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/scripts',
                component: ComponentCreator('/scripts', '09a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/scripts/duplicate-skill-loading-analysis',
                component: ComponentCreator('/scripts/duplicate-skill-loading-analysis', '7cf'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/scripts/linking-report',
                component: ComponentCreator('/scripts/linking-report', '7ac'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/scripts/linking-summary',
                component: ComponentCreator('/scripts/linking-summary', '6c0'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/scripts/phase-2-complete',
                component: ComponentCreator('/scripts/phase-2-complete', '5bb'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/troubleshooting',
                component: ComponentCreator('/troubleshooting', '98b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/troubleshooting/plugin-auto-reinstall',
                component: ComponentCreator('/troubleshooting/plugin-auto-reinstall', '13b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/troubleshooting/plugin-enabled-state-corruption',
                component: ComponentCreator('/troubleshooting/plugin-enabled-state-corruption', '10d'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/troubleshooting/plugin-naming-conventions',
                component: ComponentCreator('/troubleshooting/plugin-naming-conventions', 'f6b'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/troubleshooting/prompt-too-long-context-exhaustion',
                component: ComponentCreator('/troubleshooting/prompt-too-long-context-exhaustion', 'f29'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/troubleshooting/react-native-expo-crashes',
                component: ComponentCreator('/troubleshooting/react-native-expo-crashes', '5d8'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/troubleshooting/skill-name-prefix-stripping',
                component: ComponentCreator('/troubleshooting/skill-name-prefix-stripping', '859'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/troubleshooting/skill-truncation-budget',
                component: ComponentCreator('/troubleshooting/skill-truncation-budget', 'e9c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/troubleshooting/vscode-debug-child-processes',
                component: ComponentCreator('/troubleshooting/vscode-debug-child-processes', 'ae1'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/workflows',
                component: ComponentCreator('/workflows', 'a5d'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/workflows/brownfield',
                component: ComponentCreator('/workflows/brownfield', 'b0a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/workflows/implementation',
                component: ComponentCreator('/workflows/implementation', '2ef'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/workflows/overview',
                component: ComponentCreator('/workflows/overview', '82d'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/workflows/planning',
                component: ComponentCreator('/workflows/planning', '5e3'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/',
                component: ComponentCreator('/', 'c6e'),
                exact: true,
                sidebar: "docs"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
