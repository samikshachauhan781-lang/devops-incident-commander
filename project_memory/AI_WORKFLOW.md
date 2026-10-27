# AI Development Workflow

## Overview

This document provides guidelines for AI developers working on the DevOps Incident Commander project. It ensures consistent development practices, quality standards, and smooth handoffs between development sessions.

## Development Process

### 1. Pre-Development Preparation

#### Read Required Documents
Before starting any development work, AI developers must read and understand:

1. **NEXT_SESSION.md**: Current goals and next steps
2. **CURRENT_STATE.md**: Current project state and verified behavior
3. **TASK_TRACKER.md**: Completed, in-progress, and pending tasks
4. **FILE_MAP.md**: File responsibilities and dependencies
5. **ARCHITECTURE.md**: Technical architecture and component interactions

**Key Question**: What am I trying to accomplish? What are the current constraints?

#### Inspect Actual Code
1. **Review the code before making changes**: Read all relevant files
2. **Understand the current implementation**: Study existing patterns and conventions
3. **Check test coverage**: Ensure tests exist for the functionality you're modifying
4. **Run existing tests**: Verify current state before making changes

### 2. Development Workflow

#### Phase 1: Planning and Understanding
1. **Read all relevant memory documents**
2. **Run verification commands**:
   ```bash
   # Run specific tests for the area you're working on
   python3 -m pytest <relevant-test-file> -v

   # Run full test suite
   python3 -m pytest -x -q
   ```
3. **Identify the problem**: Clear understanding of what needs to be fixed/changed
4. **Plan the solution**: Outline the approach and expected outcomes

#### Phase 2: Implementation
1. **Make small, focused changes**: Address one issue at a time
2. **Test immediately**: Run the smallest relevant test first
3. **Verify changes**: Ensure the fix works as expected
4. **Run full test suite**: If the small test passes, run all tests
5. **Document changes**: Update relevant project memory files

#### Phase 3: Quality Assurance
1. **Review the code**: Ensure it follows project conventions
2. **Update documentation**: Keep documentation current
3. **Test thoroughly**: Run comprehensive test suite
4. **Document progress**: Update PROGRESS_LOG.md

### 3. Development Best Practices

#### Code Quality
1. **Follow existing patterns**: Match the project's coding style and conventions
2. **Write clean code**: Keep code readable and maintainable
3. **Use consistent naming**: Follow project naming conventions
4. **Add appropriate comments**: Document complex logic
5. **Handle errors properly**: Use consistent error handling patterns

#### Testing
1. **Test before fixing**: Write a failing test first
2. **Test frequently**: Run tests after each change
3. **Test edge cases**: Ensure comprehensive coverage
4. **Document tests**: Keep test coverage documented

#### Documentation
1. **Update relevant memory files**: NEXT_SESSION.md, CURRENT_STATE.md, TASK_TRACKER.md
2. **Document changes**: Add to PROGRESS_LOG.md
3. **Keep documentation current**: Ensure all documentation is up-to-date
4. **Maintain consistency**: Follow existing documentation patterns

### 4. Project Memory Files

#### Required Files
1. **NEXT_SESSION.md**: Handoff information for next session
2. **CURRENT_STATE.md**: Current project state and verified behavior
3. **TASK_TRACKER.md**: Task tracking and dependencies
4. **FILE_MAP.md**: File responsibilities and dependencies
5. **ARCHITECTURE.md**: Technical architecture and design decisions
6. **DECISIONS.md**: Technical decisions and rationale
7. **BUG_LOG.md**: Bug tracking and resolution
8. **PROGRESS_LOG.md**: Development progress tracking
9. **AI_WORKFLOW.md**: This workflow guide

#### Updating Files
- **Only update when necessary**: Don't modify files unnecessarily
- **Be specific and concise**: Focus on important changes
- **Use consistent format**: Follow existing patterns
- **Link between files**: Use references between related information

## Key Rules and Guidelines

### Never Do
1. **Skip tests**: Never skip tests or weaken assertions
2. **Delete files**: Never delete project files without good reason
3..g., Fix only the confirmed root cause. Preserve existing API behavior and test assertions.
4. **Implement new features**: Don't implement new features in this session
5. **Weaken assertions**: Never make tests weaker than required
6. **Make unrelated changes**: Only fix the issue at hand

### Always Do
1. **Read the code**: Understand the current implementation before making changes
2. **Run tests**: Verify the current state before making changes
3. **Make small changes**: Focus on one issue at a time
4. **Test thoroughly**: Run relevant tests after changes
5. **Update project memory**: Document changes in appropriate files
6. **Review the code**: Ensure changes follow project conventions

## Specific Tasks and Commands

### Running Tests
1. **Run specific tests**:
   ```bash
   # Run core functionality tests
   python3 -m pytest test_app.py -v

   # Run PATCH endpoint tests
   python3 -m pytest test_day5_patch.py -v

   # Run filtering tests
   python3 -m pytest test_day6_filters.py -v
   ```

2. **Run full test suite**:
   ```bash
   python3 -m pytest -x -q
   ```

### Development Workflow Example
```bash
# 1. Read project memory documents
# 2. Inspect relevant code
# 3. Run tests to establish baseline
cd /Users/samiksha/Desktop/devops-incident-commander
python3 -m pytest test_app.py -v

# 4. Make the specific change
cat /Users/samiksha/Desktop/devops-incident-commander/main.py | head -50

# 5. Test the change
python3 -m pytest test_app.py::test_create_valid_incident -v

# 6. Run full test suite
python3 -m pytest -x -q

# 7. Update project memory files
# 8. Document the changes
```

## Project State Management

### Task Status
- **Completed**: Task has been successfully implemented and tested
- **In Progress**: Task is currently being worked on
- **Blocked**: Task cannot proceed due to dependencies or issues
- **Pending**: Task has been identified but not yet started

### Updating Task Tracker
1. **Mark tasks as completed**: When a task is successfully implemented and tested
2. **Update task status**: Change status as tasks progress
3. **Add new tasks**: Identify and document new work
4. **Remove completed tasks**: Remove tasks that have been completed

## Example AI Development Session

### Task: Fix database transaction issue

#### Step 1: Pre-development
1. Read all project memory files
2. Inspect main.py and models.py
3. Run existing tests to establish baseline
4. Understand the problem: Database transactions not persisting data

#### Step 2: Implementation
1. Identify missing `conn.commit()` statements
2. Add explicit commits in create_incident, update_incident, delete_incident functions
3. Test the changes

#### Step 3: Verification
1. Run specific tests: `python3 -m pytest test_app.py::test_create_valid_incident -v`
2. Run full test suite: `python3 -m pytest -x -q`
3. Verify all tests pass

#### Step 4: Documentation
1. Update NEXT_SESSION.md with current status
2. Update TASK_TRACKER.md with completed task
3. Update PROGRESS_LOG.md with progress entry
4. Verify all changes are documented

## Quality Assurance

### Code Review Checklist
1. **Functionality**: Does the change work as expected?
2. **Tests**: Do all tests pass?
3. **Documentation**: Is the documentation updated?
4. **Style**: Does the code follow project conventions?
5. **Performance**: Does the change affect performance?

### Test Verification
1. **Run smallest relevant test first**
2. **Run full test suite if small test passes**
3. **Verify no regressions**
4. **Document any failures**

## Handoff Process

### Preparing for Handoff
1. **Complete all tasks**: Ensure all current tasks are completed
2. **Update all documentation**: Ensure all project memory files are current
3. **Verify all tests pass**: Run full test suite
4. **Document changes**: Add entries to PROGRESS_LOG.md
5. **Prepare next session handoff**: Update NEXT_SESSION.md

### Session Handoff
1. **Review completed work**: Assess what's been accomplished
2. **Identify remaining tasks**: Determine what's left to do
3. **Update next session goals**: Define objectives for next session
4. **Document handoff**: Update NEXT_SESSION.md with clear instructions

## Conclusion

The DevOps Incident Commander project follows a structured development workflow that ensures quality, consistency, and maintainability. By following these guidelines, AI developers can effectively contribute to the project while maintaining high standards and smooth transitions between development sessions.

**Key Principles**:
1. **Read before writing**: Understand the current state before making changes
2. **Test continuously**: Verify changes with tests
3. **Document thoroughly**: Keep all relevant project memory updated
4. **Make small changes**: Focus on one issue at a time
5. **Maintain consistency**: Follow existing patterns and conventions

**Success Metrics**:
- All tests passing (52/52)
- Comprehensive documentation
- Clean, maintainable code
- Proper project memory maintenance
- Smooth development handoffs

This workflow ensures that the project maintains high quality while allowing for efficient development and smooth transitions between AI development sessions.