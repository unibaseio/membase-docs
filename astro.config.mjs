import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://docs.membase.io',
  integrations: [
    starlight({
      title: 'Membase Docs',
      social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/unibaseio/membase-ai' }],
      sidebar: [
  {
    "label": "Overview",
    "items": [
      {
        "label": "Membase Docs",
        "link": "/"
      },
      {
        "label": "Concepts",
        "slug": "concepts"
      },
      {
        "label": "FAQ",
        "slug": "faq"
      },
      {
        "label": "What's new",
        "slug": "whats-new"
      },
      {
        "label": "Evaluation",
        "items": [
          {
            "label": "Benchmarks",
            "slug": "evaluation/benchmarks"
          }
        ]
      }
    ]
  },
  {
    "label": "Use Membase",
    "items": [
      {
        "label": "Use Membase",
        "slug": "use"
      },
      {
        "label": "Getting started",
        "items": [
          {
            "label": "Quickstart",
            "slug": "use/getting-started/quickstart"
          },
          {
            "label": "Sign in",
            "slug": "use/getting-started/sign-in"
          },
          {
            "label": "Setup guide",
            "slug": "use/getting-started/first-run-guide"
          }
        ]
      },
      {
        "label": "Bring your material in",
        "items": [
          {
            "label": "Sources",
            "slug": "use/bring-your-material-in/bring-material-in"
          },
          {
            "label": "Files",
            "slug": "use/bring-your-material-in/files"
          },
          {
            "label": "Notion",
            "slug": "use/bring-your-material-in/notion"
          },
          {
            "label": "Browser extension",
            "slug": "use/bring-your-material-in/browser-extension"
          }
        ]
      },
      {
        "label": "Manage your memory",
        "items": [
          {
            "label": "Memory",
            "slug": "use/manage-your-memory/memory"
          },
          {
            "label": "Connect",
            "slug": "use/manage-your-memory/connect"
          }
        ]
      },
      {
        "label": "Use your assistant",
        "items": [
          {
            "label": "Home",
            "slug": "use/use-your-assistant/home"
          },
          {
            "label": "Telegram",
            "slug": "use/use-your-assistant/telegram"
          }
        ]
      },
      {
        "label": "Automate and troubleshoot",
        "items": [
          {
            "label": "Schedules",
            "slug": "use/automate-and-troubleshoot/schedules"
          },
          {
            "label": "Activity",
            "slug": "use/automate-and-troubleshoot/activity"
          }
        ]
      },
      {
        "label": "Share and trade",
        "items": [
          {
            "label": "Marketplace",
            "slug": "use/share-and-trade/marketplace"
          }
        ]
      },
      {
        "label": "Account and models",
        "items": [
          {
            "label": "AI Setup",
            "slug": "use/account-and-models/ai-setup"
          },
          {
            "label": "Settings",
            "slug": "use/account-and-models/settings"
          }
        ]
      },
      {
        "label": "Advanced",
        "items": [
          {
            "label": "Studio",
            "slug": "use/advanced/studio"
          },
          {
            "label": "Agents",
            "slug": "use/advanced/agents"
          }
        ]
      }
    ]
  },
  {
    "label": "Connect your AI",
    "items": [
      {
        "label": "Connect your AI",
        "slug": "connect"
      },
      {
        "label": "Clients",
        "items": [
          {
            "label": "ChatGPT",
            "slug": "connect/clients/chatgpt"
          },
          {
            "label": "Claude",
            "slug": "connect/clients/claude"
          },
          {
            "label": "Claude Code",
            "slug": "connect/clients/claude-code"
          },
          {
            "label": "Cursor",
            "slug": "connect/clients/cursor"
          },
          {
            "label": "Codex",
            "slug": "connect/clients/codex"
          },
          {
            "label": "Grok",
            "slug": "connect/clients/grok"
          },
          {
            "label": "Kimi Code",
            "slug": "connect/clients/kimi-code"
          },
          {
            "label": "Any MCP client",
            "slug": "connect/clients/membase-mcp"
          }
        ]
      },
      {
        "label": "Manage access",
        "items": [
          {
            "label": "Access control",
            "slug": "connect/manage-access/access-control"
          },
          {
            "label": "Troubleshooting",
            "slug": "connect/manage-access/troubleshooting"
          }
        ]
      }
    ]
  },
  {
    "label": "Build with Membase",
    "items": [
      {
        "label": "Build with Membase",
        "slug": "build"
      },
      {
        "label": "Getting started",
        "items": [
          {
            "label": "Quickstart",
            "slug": "build/getting-started/api-quickstart"
          }
        ]
      },
      {
        "label": "Guides",
        "items": [
          {
            "label": "Memory operations",
            "slug": "build/guides/memory-operations"
          },
          {
            "label": "Multi-user isolation",
            "slug": "build/guides/multi-user-isolation"
          }
        ]
      },
      {
        "label": "Integrations",
        "items": [
          {
            "label": "Claude API",
            "slug": "build/integrations/claude-api"
          },
          {
            "label": "OpenAI API",
            "slug": "build/integrations/openai-api"
          },
          {
            "label": "MCP frameworks",
            "slug": "build/integrations/mcp-frameworks"
          },
          {
            "label": "AI coding assistants",
            "slug": "build/integrations/ai-coding-tools"
          }
        ]
      },
      {
        "label": "Concepts",
        "items": [
          {
            "label": "Platform overview",
            "slug": "build/concepts/platform-overview"
          },
          {
            "label": "How Membase works",
            "slug": "build/concepts/how-membase-works"
          }
        ]
      },
      {
        "label": "Reference",
        "items": [
          {
            "label": "SDKs",
            "slug": "build/reference/sdk-quickstart"
          },
          {
            "label": "Authentication",
            "slug": "build/reference/authentication"
          },
          {
            "label": "API reference",
            "slug": "build/reference/api-reference"
          },
          {
            "label": "API troubleshooting",
            "slug": "build/reference/troubleshooting"
          }
        ]
      }
    ]
  },
  {
    "label": "Resources",
    "items": [
      {
        "label": "Open Membase",
        "link": "https://www.app.membase.io"
      },
      {
        "label": "membase-ai on GitHub",
        "link": "https://github.com/unibaseio/membase-ai"
      },
      {
        "label": "Local engine reference",
        "link": "https://github.com/unibaseio/membase-ai/blob/main/docs/reference.md"
      }
    ]
  }
],
    }),
  ],
});
