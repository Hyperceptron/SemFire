## Project Management: GitHub Issues & Kanban Setup

This guide explains how to translate the project roadmap and phase plans into GitHub Issues, Milestones, Labels, and a Kanban Project Board.

### 1. Create Milestones for Each Phase
1. In your GitHub repo, go to **Settings → Milestones**.
2. Create a milestone for each phase:
   - Phase 0: Project Kickoff & Organization
   - Phase 1: Literature Survey & Data Collection
   - Phase 2: Prototype Rule-Based Detectors
   - Phase 3: ML-Based Classifiers
   - Phase 4: Integration & API Design
   - Phase 5: End-to-End Demo Application
   - Phase 6: Testing, Evaluation & Robustness
   - Phase 7: Documentation & Next Steps
3. Set target due dates and descriptions matching the roadmap.

### 2. Define Labels
Use labels to categorize work and track status.

#### Recommended Labels
- phase-0, phase-1, ..., phase-7
- area-data, area-code, area-tests, area-docs, area-demo, area-api
- status-backlog, status-in-progress, status-review, status-done
- priority-high, priority-medium, priority-low

### 3. Create Issues from Plan Tasks
1. For each Phase, create an **Epic issue** that outlines the phase objective and links to the detailed plan (e.g., `PHASE1_PLAN.md`).
2. Under each Epic, create sub-issues for each task. Example for Phase 1:
   - Issue: “Phase 1.1: Literature & Repository Survey”
   - Issue: “Phase 1.2: Define Data Schema”
   - Issue: “Phase 1.3: Implement Data Collection Script”
   - ...and so on for cleaning, splitting, verification.
3. Link each sub-issue to its Epic using GitHub’s “Linked issues” or by adding “Parent issue #<Epic number>”.
4. Assign issues to team members and attach to the corresponding milestone.

### 4. Set Up a Kanban Project Board
1. In your GitHub repo, go to **Projects** and create a new Board (e.g., “AI Deception Kanban”).
2. Create columns:
   - Backlog (status-backlog)
   - To Do (status-backlog)
   - In Progress (status-in-progress)
   - In Review (status-review)
   - Done (status-done)
3. Add automation:
   - Move issues to In Progress when an assignee is added or “in progress” label is applied.
   - Move issues to Done when closed.
4. Add all created issues to the project board and arrange them by phase/milestone.

### 5. Monitor Progress
- Use Milestones overview to track % complete per phase.
- Use the Project Board to see workflow status.
- Regularly update issue status and move cards on the board.
- Review and close issues when tasks finish.

### 6. GitHub CLI Examples (Optional)
```bash
# Create a new issue
gh issue create \
  --title "Phase 1.1: Literature & Repository Survey" \
  --body "- Review key papers: ...\n+- Inspect repos: ..." \
  --label phase-1,area-data,priority-high \
  --milestone "Phase 1: Literature Survey & Data Collection"

# Create a project board (beta)
gh project create "AI Deception Kanban" --board --repo <owner>/<repo>

# Add issue to project column
gh project item add 123 --project 456 --column "To Do"
```
*Refer to GitHub Docs for the latest UI and CLI capabilities.*

### 7. Automated GitHub Setup Script
```bash
# Export your GitHub token
export GITHUB_TOKEN=<your_token>

# Setup Phase 1 issues
scripts/github_cli.py setup --repo <owner>/<repo> --phase phase-1

# Or setup all phases
scripts/github_cli.py setup --repo <owner>/<repo> --phase all
```