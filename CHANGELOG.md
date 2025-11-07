# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

#### OneRoster CSV Output Format
- **BREAKING**: Modified CSV output format to match OneRoster 1.2 specification more strictly
  - `orgs.csv`: Replaced `metadata` column with `parentSourcedId` column
  - `users.csv`: Simplified columns - removed `orgSourcedIds`, `role`, `userIds`, `sms`, `phone`, `agents`; added `userMasterIdentifier` (lowercase sourcedId)
  - `courses.csv`: Simplified columns - removed `courseCode`, `grades`, `subjects`, `subjectCodes`, `metadata`
  - `classes.csv`: Simplified columns - removed `classCode`, `location`, `grades`, `subjects`, `periods`, `metadata`; reordered to `title`, `courseSourcedId`, `classType`, `schoolSourcedId`, `termSourcedIds`
  - `enrollments.csv`: Removed `beginDate`, `endDate`, `metadata` columns
  - `academicSessions.csv`: Removed `metadata` column
  - All CSV files: `status` and `dateLastModified` fields now output as empty strings per specification

#### Added
- `manifest.csv`: Added OneRoster 1.2 manifest file generation with proper metadata properties
- `roles.csv`: Added roles CSV file support with `OneRosterRole` model
- `OneRosterOrg` model: Added `parent_sourced_id` field for organizational hierarchy
- `OneRosterDataModel`: Added `roles` field to support role assignments

#### Models
- Added `OneRosterRole` model with fields: `sourced_id`, `status`, `date_last_modified`, `user_sourced_id`, `role_type`, `role`, `org_sourced_id`, `user_profile_sourced_id`
- Updated `OneRosterOrg` to include `parent_sourced_id` for parent organization references

#### Writers
- `write_manifest()`: New method to generate manifest.csv with OneRoster 1.2 metadata
- `write_roles()`: New method to write roles.csv file
- Updated all write methods to output empty strings for `status` and `dateLastModified` fields
- Updated `write_all()` to always generate manifest.csv and conditionally generate roles.csv

### Technical Details
- Removed unused imports: `Optional` from `oneroster_writer.py`, `UUID` from `oneroster.py`, `format_iso8601` from `converter.py`
- CSV output now strictly matches reference implementation in `RosterCSV_samples/`

## [0.1.0] - 2025-10-27

### Added

#### Core Features
- Complete SDS to OneRoster CSV conversion
- Support for all major entity types:
  - Organizations (Schools)
  - Users (Students and Teachers)
  - Courses
  - Classes
  - Enrollments
  - Academic Sessions
- UUID v5 deterministic GUID generation
- Metadata preservation with JSON format
- ISO 8601 date/datetime formatting

#### Data Models
- Pydantic-based SDS data models
- Pydantic-based OneRoster data models
- Full validation and type checking
- 35 unit tests for models (95%+ coverage)

#### Utilities
- GUID generation and validation
- Email validation
- Date validation (6 ISO 8601 formats)
- String sanitization
- Metadata JSON creation
- UserIds JSON creation
- 39 unit tests for validators (100% coverage)

#### Parsers and Writers
- SDS CSV parser with support for:
  - Schools
  - Students
  - Teachers
  - Sections
  - Enrollments (student and teacher)
- OneRoster CSV writer with support for:
  - Organizations
  - Users
  - Courses
  - Classes
  - Enrollments
  - Academic Sessions
- UTF-8 encoding support
- Automatic directory creation
- 23 unit tests for parsers/writers (97%+ coverage)

#### Converter
- Complete conversion logic
- Course deduplication from sections
- Academic session extraction
- Reference integrity maintenance
- Role mapping (student/teacher)
- 11 unit tests for converter (98.81% coverage)

#### CLI
- `convert` command - Convert SDS to OneRoster
- `validate` command - Validate SDS files
- `version` command - Show version information
- Rich terminal UI with:
  - Progress indicators
  - Colored output
  - Summary tables
- Verbose mode for detailed output
- Comprehensive error handling
- 12 unit tests for CLI (92.72% coverage)

#### Testing
- 129 total tests (100% passing)
- 120 unit tests
- 9 integration tests
- 96.94% overall code coverage
- Test fixtures for realistic data scenarios

#### CI/CD
- GitHub Actions workflows:
  - CI pipeline (Python 3.10, 3.11, 3.12)
  - Coverage reporting
  - Release automation
- Dependabot for dependency updates
- Pull request templates
- Issue templates (bug report, feature request)
- Code quality checks:
  - Black formatting
  - isort import sorting
  - Ruff linting
  - mypy type checking

#### Documentation
- Comprehensive README with:
  - Installation instructions
  - Usage examples
  - API documentation
  - Contributing guidelines
  - Quality metrics
- Project management documents:
  - Project charter
  - Technical specifications
  - Requirements analysis
  - Data mapping specification
  - Architecture design
  - Development plan
- Inline code documentation (Google style docstrings)

### Technical Details

#### Dependencies
- Python 3.10+
- Pydantic 2.x for data validation
- Typer for CLI
- Rich for terminal UI
- pytest for testing
- Black, Ruff, isort for code quality
- mypy for type checking

#### Architecture
- Layered design:
  - Models layer (SDS and OneRoster)
  - Utils layer (validators, helpers)
  - Parsers layer (CSV I/O)
  - Converter layer (transformation logic)
  - CLI layer (user interface)
- Separation of concerns
- Dependency injection friendly
- Testable components

#### Quality Metrics
- Test Coverage: 96.94%
- Total Tests: 129
- Linter Errors: 0
- Type Check Errors: 0
- Code Style: Black compliant

[Unreleased]: https://github.com/nahisaho/SDS2Roster/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nahisaho/SDS2Roster/releases/tag/v0.1.0
