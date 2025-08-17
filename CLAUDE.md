# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a multi-project repository containing various applications and tools, primarily focused on AI experiments, health tracking, web applications, and automation tools. The repository includes both Python and Node.js/TypeScript projects with different purposes and architectures.

## Key Projects

### TypeScript/React Projects (Vite + shadcn/ui)
These projects follow a consistent architecture using Vite, React, TypeScript, and shadcn/ui components:

- **health-buddie-log**: Health tracking application with data visualization
- **ltait-website**: Company/portfolio website with RSS parsing capabilities
- **little-learners-playtime-ideas**: Educational content platform
- **excel-tool**: Excel file generation and manipulation tool
- **tax-planning-tool**: Financial planning calculator
- **transfer-pricing-tool**: Business analysis tool

#### Common Commands for React/TypeScript Projects
```bash
# Development
npm run dev           # Start development server
npm run build         # Build for production
npm run lint          # Run ESLint
npm run preview       # Preview production build

# Deployment (where available)
npm run deploy        # Deploy to GitHub Pages
npm run deploy:main   # Custom deployment script (ltait-website)
```

### Python Projects
- **feminist newsletter**: Google Cloud Function for automated newsletter processing with Gmail API integration
- **blog-post-generator**: AI-powered content generation and video processing
- **health-tracker-mvp**: Health data tracking with Gemini AI integration
- **transcript**: Audio transcription utilities using Whisper

#### Common Commands for Python Projects
```bash
# Setup
pip install -r requirements.txt

# Run applications (varies by project)
python main.py                    # feminist newsletter
python run_processor.py           # blog-post-generator
python app.js                     # health-tracker-mvp (Node.js backend)
```

## Architecture Patterns

### React/TypeScript Projects
- **Stack**: Vite + React 18 + TypeScript + Tailwind CSS
- **UI Framework**: shadcn/ui with Radix UI primitives
- **Routing**: React Router DOM
- **Forms**: React Hook Form with Zod validation
- **State Management**: React Query for server state
- **Animations**: Framer Motion
- **Charts**: Recharts for data visualization

### Python Projects
- **Cloud Functions**: Google Cloud Platform integration
- **APIs**: Gmail API, Google Calendar API
- **AI Integration**: OpenAI, Google Gemini
- **Audio Processing**: OpenAI Whisper

## Common Development Patterns

1. **Component Structure**: Components are typically located in `src/components/` with co-located styles
2. **Type Safety**: Heavy use of TypeScript and Zod for runtime validation
3. **Responsive Design**: Mobile-first approach using Tailwind CSS
4. **Accessibility**: Radix UI components ensure good a11y practices
5. **Error Handling**: Toast notifications using Sonner
6. **Deployment**: Most frontend projects deploy to GitHub Pages

## Project-Specific Notes

### feminist newsletter
- Uses Google Cloud Functions (1st generation)
- Has specific troubleshooting guidelines in `.cursorrules`
- Status monitoring via `gcloud functions logs read newsletter-processor`

### health-buddie-log & ltait-website
- Use GitHub Pages deployment with custom build steps
- Include PDF generation capabilities (jsPDF, html2canvas)

### blog-post-generator
- Processes video content and generates blog posts
- Includes logging and batch processing capabilities

## Testing and Quality

- **Linting**: ESLint with TypeScript rules
- **Type Checking**: TypeScript compiler
- **No specific test framework** configured across projects (verify before assuming)

## Deployment

- **Frontend Projects**: GitHub Pages via `gh-pages` package
- **Python Projects**: Google Cloud Functions or local execution
- **Build Process**: Vite for frontend, manual deployment for Python

## Environment Setup

Most projects include configuration files for:
- **TypeScript**: `tsconfig.json`
- **ESLint**: `eslint.config.js`
- **Tailwind**: `tailwind.config.ts`
- **Vite**: `vite.config.ts`
- **PostCSS**: `postcss.config.js`

## rent-vs-buy-decision-tool Specific Rules

### Version Management (IMPORTANT)
**ALWAYS update the app version number when committing changes.** This is a strict requirement.

1. **Version Location**: Update both files when making any commit:
   - `src/app_full.py` (line ~868): Update version in header 
   - `src/app.py` (line ~29): Update version in sidebar success message

2. **Version Format**: Use semantic versioning pattern: `v2.1.x`
   - Increment patch version for fixes, features, documentation updates
   - Any commit = version bump (no exceptions)

3. **Version Description**: Include brief description of main change:
   - `v2.1.11 - Enhanced Data Tooltips`
   - `v2.1.12 - Documentation Updates`
   - `v2.1.13 - Bug Fixes`

4. **Example Version Update**:
```python
# In src/app_full.py:
<p style="color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">Executive Dashboard • Interactive Charts • [Change Description] • v2.1.X</p>

# In src/app.py:
st.sidebar.success("✅ App Updated! (v2.1.X - [Change Description])")
```

**Why This Rule Exists**: 
- Users need to see app updates in production
- Helps track which version is deployed
- Prevents confusion about whether changes are live
- Maintains clear deployment history

**No Exceptions**: Every commit must include a version bump, even for documentation or small fixes.

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

      
      IMPORTANT: this context may or may not be relevant to your tasks. You should not respond to this context unless it is highly relevant to your task.