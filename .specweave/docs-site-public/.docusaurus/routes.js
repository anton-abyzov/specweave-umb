import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '/',
    component: ComponentCreator('/', '36f'),
    routes: [
      {
        path: '/',
        component: ComponentCreator('/', '5ab'),
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
            component: ComponentCreator('/', '2de'),
            routes: [
              {
                path: '/academy/',
                component: ComponentCreator('/academy/', 'dfe'),
                exact: true
              },
              {
                path: '/academy/videos/_TEMPLATE',
                component: ComponentCreator('/academy/videos/_TEMPLATE', '5aa'),
                exact: true
              },
              {
                path: '/academy/videos/clawhub-postmortem',
                component: ComponentCreator('/academy/videos/clawhub-postmortem', 'ca8'),
                exact: true
              },
              {
                path: '/academy/videos/specweave-complete-masterclass',
                component: ComponentCreator('/academy/videos/specweave-complete-masterclass', '570'),
                exact: true
              },
              {
                path: '/academy/videos/stop-repeating-yourself',
                component: ComponentCreator('/academy/videos/stop-repeating-yourself', '4ee'),
                exact: true
              },
              {
                path: '/academy/videos/toxicskills-security',
                component: ComponentCreator('/academy/videos/toxicskills-security', '147'),
                exact: true
              },
              {
                path: '/api/',
                component: ComponentCreator('/api/', 'd93'),
                exact: true
              },
              {
                path: '/commands',
                component: ComponentCreator('/commands', '887'),
                exact: true
              },
              {
                path: '/commands/abandon',
                component: ComponentCreator('/commands/abandon', '7f7'),
                exact: true
              },
              {
                path: '/commands/auto',
                component: ComponentCreator('/commands/auto', 'bf0'),
                exact: true
              },
              {
                path: '/commands/auto-status',
                component: ComponentCreator('/commands/auto-status', '7b5'),
                exact: true
              },
              {
                path: '/commands/cancel-auto',
                component: ComponentCreator('/commands/cancel-auto', '7a2'),
                exact: true
              },
              {
                path: '/commands/do',
                component: ComponentCreator('/commands/do', 'fb3'),
                exact: true
              },
              {
                path: '/commands/jobs',
                component: ComponentCreator('/commands/jobs', 'a28'),
                exact: true
              },
              {
                path: '/commands/overview',
                component: ComponentCreator('/commands/overview', 'eb5'),
                exact: true
              },
              {
                path: '/commands/pause',
                component: ComponentCreator('/commands/pause', '949'),
                exact: true
              },
              {
                path: '/commands/resume',
                component: ComponentCreator('/commands/resume', '495'),
                exact: true
              },
              {
                path: '/commands/status',
                component: ComponentCreator('/commands/status', '60f'),
                exact: true
              },
              {
                path: '/commands/status-management',
                component: ComponentCreator('/commands/status-management', '928'),
                exact: true
              },
              {
                path: '/development',
                component: ComponentCreator('/development', '21d'),
                exact: true
              },
              {
                path: '/development/claude-cli-automation',
                component: ComponentCreator('/development/claude-cli-automation', 'af1'),
                exact: true
              },
              {
                path: '/faq',
                component: ComponentCreator('/faq', '8be'),
                exact: true
              },
              {
                path: '/features',
                component: ComponentCreator('/features', '211'),
                exact: true
              },
              {
                path: '/glossary/',
                component: ComponentCreator('/glossary/', '63f'),
                exact: true
              },
              {
                path: '/glossary/categories/architecture-category',
                component: ComponentCreator('/glossary/categories/architecture-category', '55f'),
                exact: true
              },
              {
                path: '/glossary/categories/backend-category',
                component: ComponentCreator('/glossary/categories/backend-category', 'cd6'),
                exact: true
              },
              {
                path: '/glossary/categories/category-pages-complete',
                component: ComponentCreator('/glossary/categories/category-pages-complete', '2b1'),
                exact: true
              },
              {
                path: '/glossary/categories/collaboration-category',
                component: ComponentCreator('/glossary/categories/collaboration-category', 'ba9'),
                exact: true
              },
              {
                path: '/glossary/categories/devops-category',
                component: ComponentCreator('/glossary/categories/devops-category', 'aa3'),
                exact: true
              },
              {
                path: '/glossary/categories/frontend-category',
                component: ComponentCreator('/glossary/categories/frontend-category', '95f'),
                exact: true
              },
              {
                path: '/glossary/categories/infrastructure-category',
                component: ComponentCreator('/glossary/categories/infrastructure-category', '0ed'),
                exact: true
              },
              {
                path: '/glossary/categories/ml-ai-category',
                component: ComponentCreator('/glossary/categories/ml-ai-category', 'e40'),
                exact: true
              },
              {
                path: '/glossary/categories/performance-category',
                component: ComponentCreator('/glossary/categories/performance-category', 'bf5'),
                exact: true
              },
              {
                path: '/glossary/categories/testing-category',
                component: ComponentCreator('/glossary/categories/testing-category', 'eca'),
                exact: true
              },
              {
                path: '/glossary/index-by-category',
                component: ComponentCreator('/glossary/index-by-category', 'c4b'),
                exact: true
              },
              {
                path: '/glossary/terms/ac-id',
                component: ComponentCreator('/glossary/terms/ac-id', '8a0'),
                exact: true
              },
              {
                path: '/glossary/terms/acceptance-criteria',
                component: ComponentCreator('/glossary/terms/acceptance-criteria', '5b5'),
                exact: true
              },
              {
                path: '/glossary/terms/adr',
                component: ComponentCreator('/glossary/terms/adr', '11f'),
                exact: true
              },
              {
                path: '/glossary/terms/angular',
                component: ComponentCreator('/glossary/terms/angular', '0a0'),
                exact: true
              },
              {
                path: '/glossary/terms/api',
                component: ComponentCreator('/glossary/terms/api', '037'),
                exact: true
              },
              {
                path: '/glossary/terms/bdd',
                component: ComponentCreator('/glossary/terms/bdd', '83e'),
                exact: true
              },
              {
                path: '/glossary/terms/bidirectional-sync',
                component: ComponentCreator('/glossary/terms/bidirectional-sync', 'a1d'),
                exact: true
              },
              {
                path: '/glossary/terms/brownfield',
                component: ComponentCreator('/glossary/terms/brownfield', '4c2'),
                exact: true
              },
              {
                path: '/glossary/terms/ci-cd',
                component: ComponentCreator('/glossary/terms/ci-cd', 'f1c'),
                exact: true
              },
              {
                path: '/glossary/terms/content-classification',
                component: ComponentCreator('/glossary/terms/content-classification', 'f8d'),
                exact: true
              },
              {
                path: '/glossary/terms/copied-acs-and-tasks',
                component: ComponentCreator('/glossary/terms/copied-acs-and-tasks', 'de8'),
                exact: true
              },
              {
                path: '/glossary/terms/cross-linking',
                component: ComponentCreator('/glossary/terms/cross-linking', '66b'),
                exact: true
              },
              {
                path: '/glossary/terms/docker',
                component: ComponentCreator('/glossary/terms/docker', '038'),
                exact: true
              },
              {
                path: '/glossary/terms/docusaurus-frontmatter',
                component: ComponentCreator('/glossary/terms/docusaurus-frontmatter', 'e6b'),
                exact: true
              },
              {
                path: '/glossary/terms/e2e',
                component: ComponentCreator('/glossary/terms/e2e', '48e'),
                exact: true
              },
              {
                path: '/glossary/terms/fda',
                component: ComponentCreator('/glossary/terms/fda', '97d'),
                exact: true
              },
              {
                path: '/glossary/terms/git',
                component: ComponentCreator('/glossary/terms/git', '244'),
                exact: true
              },
              {
                path: '/glossary/terms/github-actions',
                component: ComponentCreator('/glossary/terms/github-actions', '12e'),
                exact: true
              },
              {
                path: '/glossary/terms/graphql',
                component: ComponentCreator('/glossary/terms/graphql', '8d6'),
                exact: true
              },
              {
                path: '/glossary/terms/greenfield',
                component: ComponentCreator('/glossary/terms/greenfield', 'd2c'),
                exact: true
              },
              {
                path: '/glossary/terms/hipaa',
                component: ComponentCreator('/glossary/terms/hipaa', '941'),
                exact: true
              },
              {
                path: '/glossary/terms/hooks',
                component: ComponentCreator('/glossary/terms/hooks', 'b47'),
                exact: true
              },
              {
                path: '/glossary/terms/iac',
                component: ComponentCreator('/glossary/terms/iac', '196'),
                exact: true
              },
              {
                path: '/glossary/terms/increments',
                component: ComponentCreator('/glossary/terms/increments', '8d0'),
                exact: true
              },
              {
                path: '/glossary/terms/integration-testing',
                component: ComponentCreator('/glossary/terms/integration-testing', 'e93'),
                exact: true
              },
              {
                path: '/glossary/terms/intelligent-living-docs-sync',
                component: ComponentCreator('/glossary/terms/intelligent-living-docs-sync', 'e0a'),
                exact: true
              },
              {
                path: '/glossary/terms/kubernetes',
                component: ComponentCreator('/glossary/terms/kubernetes', '873'),
                exact: true
              },
              {
                path: '/glossary/terms/living-docs',
                component: ComponentCreator('/glossary/terms/living-docs', '7d6'),
                exact: true
              },
              {
                path: '/glossary/terms/microservices',
                component: ComponentCreator('/glossary/terms/microservices', 'ffc'),
                exact: true
              },
              {
                path: '/glossary/terms/monolith',
                component: ComponentCreator('/glossary/terms/monolith', '19d'),
                exact: true
              },
              {
                path: '/glossary/terms/nextjs',
                component: ComponentCreator('/glossary/terms/nextjs', '10e'),
                exact: true
              },
              {
                path: '/glossary/terms/nodejs',
                component: ComponentCreator('/glossary/terms/nodejs', 'f1d'),
                exact: true
              },
              {
                path: '/glossary/terms/playwright',
                component: ComponentCreator('/glossary/terms/playwright', 'bcf'),
                exact: true
              },
              {
                path: '/glossary/terms/profile-based-sync',
                component: ComponentCreator('/glossary/terms/profile-based-sync', 'cbd'),
                exact: true
              },
              {
                path: '/glossary/terms/project-detection',
                component: ComponentCreator('/glossary/terms/project-detection', '94d'),
                exact: true
              },
              {
                path: '/glossary/terms/project-specific-tasks',
                component: ComponentCreator('/glossary/terms/project-specific-tasks', '492'),
                exact: true
              },
              {
                path: '/glossary/terms/react',
                component: ComponentCreator('/glossary/terms/react', '76c'),
                exact: true
              },
              {
                path: '/glossary/terms/rest',
                component: ComponentCreator('/glossary/terms/rest', '66f'),
                exact: true
              },
              {
                path: '/glossary/terms/rfc',
                component: ComponentCreator('/glossary/terms/rfc', '7d1'),
                exact: true
              },
              {
                path: '/glossary/terms/role-orchestrator',
                component: ComponentCreator('/glossary/terms/role-orchestrator', '207'),
                exact: true
              },
              {
                path: '/glossary/terms/skills-vs-agents',
                component: ComponentCreator('/glossary/terms/skills-vs-agents', '197'),
                exact: true
              },
              {
                path: '/glossary/terms/soc2',
                component: ComponentCreator('/glossary/terms/soc2', 'a00'),
                exact: true
              },
              {
                path: '/glossary/terms/source-of-truth',
                component: ComponentCreator('/glossary/terms/source-of-truth', '6d8'),
                exact: true
              },
              {
                path: '/glossary/terms/spa',
                component: ComponentCreator('/glossary/terms/spa', '126'),
                exact: true
              },
              {
                path: '/glossary/terms/specs',
                component: ComponentCreator('/glossary/terms/specs', '070'),
                exact: true
              },
              {
                path: '/glossary/terms/ssg',
                component: ComponentCreator('/glossary/terms/ssg', 'c1f'),
                exact: true
              },
              {
                path: '/glossary/terms/ssr',
                component: ComponentCreator('/glossary/terms/ssr', '8b7'),
                exact: true
              },
              {
                path: '/glossary/terms/strategic-init',
                component: ComponentCreator('/glossary/terms/strategic-init', '405'),
                exact: true
              },
              {
                path: '/glossary/terms/tdd',
                component: ComponentCreator('/glossary/terms/tdd', 'e41'),
                exact: true
              },
              {
                path: '/glossary/terms/terraform',
                component: ComponentCreator('/glossary/terms/terraform', 'c80'),
                exact: true
              },
              {
                path: '/glossary/terms/test-coverage',
                component: ComponentCreator('/glossary/terms/test-coverage', 'a95'),
                exact: true
              },
              {
                path: '/glossary/terms/test-pyramid',
                component: ComponentCreator('/glossary/terms/test-pyramid', 'e91'),
                exact: true
              },
              {
                path: '/glossary/terms/three-layer-architecture',
                component: ComponentCreator('/glossary/terms/three-layer-architecture', '441'),
                exact: true
              },
              {
                path: '/glossary/terms/three-permission-architecture',
                component: ComponentCreator('/glossary/terms/three-permission-architecture', '23a'),
                exact: true
              },
              {
                path: '/glossary/terms/typescript',
                component: ComponentCreator('/glossary/terms/typescript', '6dd'),
                exact: true
              },
              {
                path: '/glossary/terms/unit-testing',
                component: ComponentCreator('/glossary/terms/unit-testing', '03b'),
                exact: true
              },
              {
                path: '/glossary/terms/user-stories',
                component: ComponentCreator('/glossary/terms/user-stories', '49a'),
                exact: true
              },
              {
                path: '/glossary/terms/wip-limits',
                component: ComponentCreator('/glossary/terms/wip-limits', '776'),
                exact: true
              },
              {
                path: '/guides',
                component: ComponentCreator('/guides', '7aa'),
                exact: true
              },
              {
                path: '/guides/ado-multi-project-migration',
                component: ComponentCreator('/guides/ado-multi-project-migration', '7ef'),
                exact: true
              },
              {
                path: '/guides/autonomous-execution',
                component: ComponentCreator('/guides/autonomous-execution', '606'),
                exact: true
              },
              {
                path: '/guides/backlog-management',
                component: ComponentCreator('/guides/backlog-management', '305'),
                exact: true
              },
              {
                path: '/guides/best-practices',
                component: ComponentCreator('/guides/best-practices', '75f'),
                exact: true
              },
              {
                path: '/guides/bidirectional-linking',
                component: ComponentCreator('/guides/bidirectional-linking', 'ca7'),
                exact: true
              },
              {
                path: '/guides/command-reference-by-priority',
                component: ComponentCreator('/guides/command-reference-by-priority', '8e3'),
                exact: true
              },
              {
                path: '/guides/compliance-standards',
                component: ComponentCreator('/guides/compliance-standards', 'c10'),
                exact: true
              },
              {
                path: '/guides/core-concepts/background-jobs',
                component: ComponentCreator('/guides/core-concepts/background-jobs', 'f60'),
                exact: true
              },
              {
                path: '/guides/core-concepts/living-docs-sync-strategy',
                component: ComponentCreator('/guides/core-concepts/living-docs-sync-strategy', '3f0'),
                exact: true
              },
              {
                path: '/guides/core-concepts/living-documentation',
                component: ComponentCreator('/guides/core-concepts/living-documentation', '3df'),
                exact: true
              },
              {
                path: '/guides/core-concepts/what-is-an-increment',
                component: ComponentCreator('/guides/core-concepts/what-is-an-increment', '4d8'),
                exact: true
              },
              {
                path: '/guides/cost-optimization',
                component: ComponentCreator('/guides/cost-optimization', '87e'),
                exact: true
              },
              {
                path: '/guides/deep-interview-mode',
                component: ComponentCreator('/guides/deep-interview-mode', 'e13'),
                exact: true
              },
              {
                path: '/guides/getting-started/installation',
                component: ComponentCreator('/guides/getting-started/installation', '4a6'),
                exact: true
              },
              {
                path: '/guides/getting-started/nvm-global-packages-fix',
                component: ComponentCreator('/guides/getting-started/nvm-global-packages-fix', '5c8'),
                exact: true
              },
              {
                path: '/guides/getting-started/quickstart',
                component: ComponentCreator('/guides/getting-started/quickstart', '30c'),
                exact: true
              },
              {
                path: '/guides/github-action-setup',
                component: ComponentCreator('/guides/github-action-setup', 'e80'),
                exact: true
              },
              {
                path: '/guides/github-integration',
                component: ComponentCreator('/guides/github-integration', 'a68'),
                exact: true
              },
              {
                path: '/guides/hierarchy-mapping',
                component: ComponentCreator('/guides/hierarchy-mapping', '9b0'),
                exact: true
              },
              {
                path: '/guides/increment-status-reference',
                component: ComponentCreator('/guides/increment-status-reference', '443'),
                exact: true
              },
              {
                path: '/guides/intelligent-living-docs-sync',
                component: ComponentCreator('/guides/intelligent-living-docs-sync', 'a27'),
                exact: true
              },
              {
                path: '/guides/kafka-advanced-usage',
                component: ComponentCreator('/guides/kafka-advanced-usage', '4a6'),
                exact: true
              },
              {
                path: '/guides/kafka-getting-started',
                component: ComponentCreator('/guides/kafka-getting-started', '730'),
                exact: true
              },
              {
                path: '/guides/kafka-terraform',
                component: ComponentCreator('/guides/kafka-terraform', 'c11'),
                exact: true
              },
              {
                path: '/guides/kafka-troubleshooting',
                component: ComponentCreator('/guides/kafka-troubleshooting', '79f'),
                exact: true
              },
              {
                path: '/guides/meta-capability',
                component: ComponentCreator('/guides/meta-capability', '24a'),
                exact: true
              },
              {
                path: '/guides/migration-v024',
                component: ComponentCreator('/guides/migration-v024', '807'),
                exact: true
              },
              {
                path: '/guides/migration-v031-project-fields',
                component: ComponentCreator('/guides/migration-v031-project-fields', 'c25'),
                exact: true
              },
              {
                path: '/guides/mobile/react-native-setup-guide',
                component: ComponentCreator('/guides/mobile/react-native-setup-guide', 'bc7'),
                exact: true
              },
              {
                path: '/guides/model-selection',
                component: ComponentCreator('/guides/model-selection', '02b'),
                exact: true
              },
              {
                path: '/guides/multi-project-setup',
                component: ComponentCreator('/guides/multi-project-setup', '213'),
                exact: true
              },
              {
                path: '/guides/multi-project-sync-architecture',
                component: ComponentCreator('/guides/multi-project-sync-architecture', '46f'),
                exact: true
              },
              {
                path: '/guides/multilingual-guide',
                component: ComponentCreator('/guides/multilingual-guide', 'beb'),
                exact: true
              },
              {
                path: '/guides/openclaw-agent-setup',
                component: ComponentCreator('/guides/openclaw-agent-setup', '6a1'),
                exact: true
              },
              {
                path: '/guides/plugin-management',
                component: ComponentCreator('/guides/plugin-management', 'a8b'),
                exact: true
              },
              {
                path: '/guides/project-specific-tasks',
                component: ComponentCreator('/guides/project-specific-tasks', '314'),
                exact: true
              },
              {
                path: '/guides/repository-selection',
                component: ComponentCreator('/guides/repository-selection', '668'),
                exact: true
              },
              {
                path: '/guides/scheduling-and-planning',
                component: ComponentCreator('/guides/scheduling-and-planning', '372'),
                exact: true
              },
              {
                path: '/guides/spec-bidirectional-sync',
                component: ComponentCreator('/guides/spec-bidirectional-sync', 'dab'),
                exact: true
              },
              {
                path: '/guides/spec-commit-sync',
                component: ComponentCreator('/guides/spec-commit-sync', 'c20'),
                exact: true
              },
              {
                path: '/guides/specs-organization-guide',
                component: ComponentCreator('/guides/specs-organization-guide', 'fa2'),
                exact: true
              },
              {
                path: '/guides/specweave-vs-speckit',
                component: ComponentCreator('/guides/specweave-vs-speckit', '788'),
                exact: true
              },
              {
                path: '/guides/status-sync-guide',
                component: ComponentCreator('/guides/status-sync-guide', '1b8'),
                exact: true
              },
              {
                path: '/guides/status-sync-migration',
                component: ComponentCreator('/guides/status-sync-migration', '6f9'),
                exact: true
              },
              {
                path: '/guides/strategic-init',
                component: ComponentCreator('/guides/strategic-init', '0f7'),
                exact: true
              },
              {
                path: '/guides/sync-configuration',
                component: ComponentCreator('/guides/sync-configuration', '28c'),
                exact: true
              },
              {
                path: '/guides/sync-strategies',
                component: ComponentCreator('/guides/sync-strategies', '6d7'),
                exact: true
              },
              {
                path: '/guides/why-verified-skill-matters',
                component: ComponentCreator('/guides/why-verified-skill-matters', '2d0'),
                exact: true
              },
              {
                path: '/integrations',
                component: ComponentCreator('/integrations', '60f'),
                exact: true
              },
              {
                path: '/integrations/generic-ai-tools',
                component: ComponentCreator('/integrations/generic-ai-tools', '811'),
                exact: true
              },
              {
                path: '/integrations/issue-trackers',
                component: ComponentCreator('/integrations/issue-trackers', '3bf'),
                exact: true
              },
              {
                path: '/learn',
                component: ComponentCreator('/learn', 'dc6'),
                exact: true
              },
              {
                path: '/learn/backend/backend-fundamentals',
                component: ComponentCreator('/learn/backend/backend-fundamentals', 'db4'),
                exact: true
              },
              {
                path: '/learn/foundations/claude-code-basics',
                component: ComponentCreator('/learn/foundations/claude-code-basics', '9ce'),
                exact: true
              },
              {
                path: '/learn/foundations/enterprise-app-development',
                component: ComponentCreator('/learn/foundations/enterprise-app-development', '653'),
                exact: true
              },
              {
                path: '/learn/foundations/software-engineering-roles',
                component: ComponentCreator('/learn/foundations/software-engineering-roles', '02a'),
                exact: true
              },
              {
                path: '/learn/foundations/terminal-empowerment',
                component: ComponentCreator('/learn/foundations/terminal-empowerment', 'd44'),
                exact: true
              },
              {
                path: '/learn/frontend/frontend-fundamentals',
                component: ComponentCreator('/learn/frontend/frontend-fundamentals', '74b'),
                exact: true
              },
              {
                path: '/learn/infrastructure/iac-fundamentals',
                component: ComponentCreator('/learn/infrastructure/iac-fundamentals', 'ae4'),
                exact: true
              },
              {
                path: '/learn/ml-ai/ml-fundamentals',
                component: ComponentCreator('/learn/ml-ai/ml-fundamentals', '5ad'),
                exact: true
              },
              {
                path: '/learn/testing/cli-integration-testing',
                component: ComponentCreator('/learn/testing/cli-integration-testing', '5d8'),
                exact: true
              },
              {
                path: '/learn/testing/testing-fundamentals',
                component: ComponentCreator('/learn/testing/testing-fundamentals', 'c2b'),
                exact: true
              },
              {
                path: '/marketing',
                component: ComponentCreator('/marketing', '9f8'),
                exact: true
              },
              {
                path: '/marketing/dev-to-article-clean',
                component: ComponentCreator('/marketing/dev-to-article-clean', '0ea'),
                exact: true
              },
              {
                path: '/marketing/hooks-skill-workaround-posts',
                component: ComponentCreator('/marketing/hooks-skill-workaround-posts', '6fc'),
                exact: true
              },
              {
                path: '/marketing/thariq-skills-response',
                component: ComponentCreator('/marketing/thariq-skills-response', '473'),
                exact: true
              },
              {
                path: '/marketing/toxicskills-security-posts',
                component: ComponentCreator('/marketing/toxicskills-security-posts', '933'),
                exact: true
              },
              {
                path: '/metrics',
                component: ComponentCreator('/metrics', 'b43'),
                exact: true
              },
              {
                path: '/overview',
                component: ComponentCreator('/overview', 'de8'),
                exact: true
              },
              {
                path: '/overview/features',
                component: ComponentCreator('/overview/features', '444'),
                exact: true
              },
              {
                path: '/overview/introduction',
                component: ComponentCreator('/overview/introduction', '053'),
                exact: true
              },
              {
                path: '/overview/philosophy',
                component: ComponentCreator('/overview/philosophy', 'bed'),
                exact: true
              },
              {
                path: '/overview/plugins-ecosystem',
                component: ComponentCreator('/overview/plugins-ecosystem', 'e6b'),
                exact: true
              },
              {
                path: '/reference',
                component: ComponentCreator('/reference', 'dc2'),
                exact: true
              },
              {
                path: '/reference/cost-tracking',
                component: ComponentCreator('/reference/cost-tracking', '186'),
                exact: true
              },
              {
                path: '/scripts',
                component: ComponentCreator('/scripts', '088'),
                exact: true
              },
              {
                path: '/scripts/duplicate-skill-loading-analysis',
                component: ComponentCreator('/scripts/duplicate-skill-loading-analysis', 'e10'),
                exact: true
              },
              {
                path: '/scripts/linking-report',
                component: ComponentCreator('/scripts/linking-report', 'bfa'),
                exact: true
              },
              {
                path: '/scripts/linking-summary',
                component: ComponentCreator('/scripts/linking-summary', '6d6'),
                exact: true
              },
              {
                path: '/scripts/phase-2-complete',
                component: ComponentCreator('/scripts/phase-2-complete', 'b22'),
                exact: true
              },
              {
                path: '/troubleshooting',
                component: ComponentCreator('/troubleshooting', 'a5a'),
                exact: true
              },
              {
                path: '/troubleshooting/plugin-auto-reinstall',
                component: ComponentCreator('/troubleshooting/plugin-auto-reinstall', 'b82'),
                exact: true
              },
              {
                path: '/troubleshooting/plugin-enabled-state-corruption',
                component: ComponentCreator('/troubleshooting/plugin-enabled-state-corruption', '9cc'),
                exact: true
              },
              {
                path: '/troubleshooting/plugin-naming-conventions',
                component: ComponentCreator('/troubleshooting/plugin-naming-conventions', '502'),
                exact: true
              },
              {
                path: '/troubleshooting/prompt-too-long-context-exhaustion',
                component: ComponentCreator('/troubleshooting/prompt-too-long-context-exhaustion', '928'),
                exact: true
              },
              {
                path: '/troubleshooting/react-native-expo-crashes',
                component: ComponentCreator('/troubleshooting/react-native-expo-crashes', 'cae'),
                exact: true
              },
              {
                path: '/troubleshooting/skill-name-prefix-stripping',
                component: ComponentCreator('/troubleshooting/skill-name-prefix-stripping', '425'),
                exact: true
              },
              {
                path: '/troubleshooting/skill-truncation-budget',
                component: ComponentCreator('/troubleshooting/skill-truncation-budget', '5bc'),
                exact: true
              },
              {
                path: '/troubleshooting/vscode-debug-child-processes',
                component: ComponentCreator('/troubleshooting/vscode-debug-child-processes', 'a6d'),
                exact: true
              },
              {
                path: '/workflows',
                component: ComponentCreator('/workflows', '8a0'),
                exact: true
              },
              {
                path: '/workflows/brownfield',
                component: ComponentCreator('/workflows/brownfield', '051'),
                exact: true
              },
              {
                path: '/workflows/implementation',
                component: ComponentCreator('/workflows/implementation', '573'),
                exact: true
              },
              {
                path: '/workflows/overview',
                component: ComponentCreator('/workflows/overview', 'bc5'),
                exact: true
              },
              {
                path: '/workflows/planning',
                component: ComponentCreator('/workflows/planning', '81b'),
                exact: true
              },
              {
                path: '/',
                component: ComponentCreator('/', '408'),
                exact: true
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
