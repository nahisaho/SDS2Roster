"""Command-line interface for SDS2Roster."""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from sds2roster import __version__
from sds2roster.converter import SDSToOneRosterConverter
from sds2roster.parsers.oneroster_writer import OneRosterCSVWriter
from sds2roster.parsers.sds_parser import SDSCSVParser

app = typer.Typer(
    name="sds2roster",
    help="Microsoft SDS to OneRoster CSV converter",
    add_completion=False,
)
azure_app = typer.Typer(help="Azure integration commands")
app.add_typer(azure_app, name="azure")
console = Console()


def _validate_input_directory(input_path: Path) -> None:
    """Validate that the input directory exists and is a directory."""
    if not input_path.exists():
        console.print(f"[red]Error: Input directory not found: {input_path}[/red]")
        raise typer.Exit(code=1)

    if not input_path.is_dir():
        console.print(f"[red]Error: Input path is not a directory: {input_path}[/red]")
        raise typer.Exit(code=1)


def _check_required_files(input_path: Path) -> list[str]:
    """Check for required SDS files and return list of missing files."""
    required_files = [
        "school.csv",
        "student.csv",
        "teacher.csv",
        "section.csv",
        "studentEnrollment.csv",
        "teacherRoster.csv",
    ]

    missing_files = []
    for file in required_files:
        if not (input_path / file).exists():
            missing_files.append(file)

    return missing_files


def _display_missing_files_error(missing_files: list[str]) -> None:
    """Display error message for missing files."""
    console.print("[red]Error: Missing required SDS files:[/red]")
    for file in missing_files:
        console.print(f"  - {file}")


def _check_and_display_files(input_path: Path) -> tuple[list[str], list[str]]:
    """Check required files and display status. Returns (missing_files, found_files)."""
    required_files = [
        "school.csv",
        "student.csv",
        "teacher.csv",
        "section.csv",
        "studentEnrollment.csv",
        "teacherRoster.csv",
    ]

    console.print("[cyan]Checking required files...[/cyan]")
    missing_files = []
    found_files = []

    for file in required_files:
        if (input_path / file).exists():
            found_files.append(file)
            console.print(f"  [green]OK[/green] {file}")
        else:
            missing_files.append(file)
            console.print(f"  [red]MISSING[/red] {file} (missing)")

    console.print()
    return missing_files, found_files


@app.command()
def convert(
    input_path: Path = typer.Argument(..., help="Path to SDS CSV files directory"),
    output_path: Path = typer.Argument(..., help="Path to output OneRoster CSV files"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate data"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Convert SDS CSV files to OneRoster format.

    This command reads Microsoft SDS CSV files from the input directory,
    converts them to OneRoster v1.2 format, and writes the output to the
    specified directory.

    Example:
        sds2roster convert ./sds_data ./oneroster_output
    """
    console.print(f"[bold blue]SDS2Roster v{__version__}[/bold blue]")
    console.print()

    # Validate input directory
    _validate_input_directory(input_path)
    
    # Ensure output path is absolute
    output_path = output_path.absolute()

    # Check for required SDS files
    missing_files = _check_required_files(input_path)

    if missing_files:
        _display_missing_files_error(missing_files)
        raise typer.Exit(code=1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Parse SDS files
            task = progress.add_task("[cyan]Parsing SDS CSV files...", total=None)
            parser = SDSCSVParser()
            sds_data = parser.parse_all(
                school_file=input_path / "school.csv",
                student_file=input_path / "student.csv",
                teacher_file=input_path / "teacher.csv",
                section_file=input_path / "section.csv",
                student_enrollment_file=input_path / "studentEnrollment.csv",
                teacher_roster_file=input_path / "teacherRoster.csv",
            )
            progress.update(task, completed=True)

            if verbose:
                console.print(f"  Parsed {len(sds_data.schools)} schools")
                console.print(f"  Parsed {len(sds_data.students)} students")
                console.print(f"  Parsed {len(sds_data.teachers)} teachers")
                console.print(f"  Parsed {len(sds_data.sections)} sections")
                console.print(f"  Parsed {len(sds_data.enrollments)} enrollments")
                console.print()

            # Convert to OneRoster
            task = progress.add_task("[cyan]Converting to OneRoster format...", total=None)
            converter = SDSToOneRosterConverter()
            oneroster_data = converter.convert(sds_data)
            progress.update(task, completed=True)

            if verbose:
                console.print(f"  Generated {len(oneroster_data.orgs)} organizations")
                console.print(f"  Generated {len(oneroster_data.users)} users")
                console.print(f"  Generated {len(oneroster_data.courses)} courses")
                console.print(f"  Generated {len(oneroster_data.classes)} classes")
                console.print(f"  Generated {len(oneroster_data.enrollments)} enrollments")
                console.print(
                    f"  Generated {len(oneroster_data.academic_sessions)} academic sessions"
                )
                console.print()

            # Write OneRoster files
            task = progress.add_task("[cyan]Writing OneRoster CSV files...", total=None)
            writer = OneRosterCSVWriter(output_path)
            writer.write_all(oneroster_data)
            progress.update(task, completed=True)

        # Success summary
        console.print()
        console.print("[bold green]Conversion completed successfully![/bold green]")
        console.print()

        # Display summary table
        table = Table(title="Conversion Summary")
        table.add_column("Entity Type", style="cyan")
        table.add_column("Count", style="green", justify="right")

        table.add_row("Organizations", str(len(oneroster_data.orgs)))
        table.add_row("Users", str(len(oneroster_data.users)))
        table.add_row("Courses", str(len(oneroster_data.courses)))
        table.add_row("Classes", str(len(oneroster_data.classes)))
        table.add_row("Enrollments", str(len(oneroster_data.enrollments)))
        table.add_row("Academic Sessions", str(len(oneroster_data.academic_sessions)))

        console.print(table)
        console.print()
        console.print(f"Output written to: [bold]{output_path}[/bold]")

    except FileNotFoundError as e:
        console.print(f"[red]Error: File not found: {e}[/red]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]Error during conversion: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from e


@app.command()
def validate(
    input_path: Path = typer.Argument(..., help="Path to SDS CSV files directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Validate SDS CSV files.

    This command checks if all required SDS CSV files exist and can be parsed
    without errors. It does not perform conversion.

    Example:
        sds2roster validate ./sds_data
    """
    console.print("[bold blue]Validating SDS files...[/bold blue]")
    console.print()

    # Validate input directory
    _validate_input_directory(input_path)

    # Check for required SDS files
    missing_files, found_files = _check_and_display_files(input_path)

    if missing_files:
        console.print("[red]Validation failed: Missing required files[/red]")
        raise typer.Exit(code=1)

    # Try to parse files
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Parsing SDS CSV files...", total=None)
            parser = SDSCSVParser()
            sds_data = parser.parse_all(
                school_file=input_path / "school.csv",
                student_file=input_path / "student.csv",
                teacher_file=input_path / "teacher.csv",
                section_file=input_path / "section.csv",
                student_enrollment_file=input_path / "studentEnrollment.csv",
                teacher_roster_file=input_path / "teacherRoster.csv",
            )
            progress.update(task, completed=True)

        # Display validation results
        console.print()
        console.print("[bold green]All files validated successfully![/bold green]")
        console.print()

        # Display statistics table
        table = Table(title="Validation Summary")
        table.add_column("Entity Type", style="cyan")
        table.add_column("Count", style="green", justify="right")

        table.add_row("Schools", str(len(sds_data.schools)))
        table.add_row("Students", str(len(sds_data.students)))
        table.add_row("Teachers", str(len(sds_data.teachers)))
        table.add_row("Sections", str(len(sds_data.sections)))
        table.add_row("Enrollments", str(len(sds_data.enrollments)))

        console.print(table)

        if verbose:
            console.print()
            console.print("[cyan]Detailed Statistics:[/cyan]")
            console.print(
                f"  Student enrollments: {len([e for e in sds_data.enrollments if e.role == 'student'])}"
            )
            console.print(
                f"  Teacher enrollments: {len([e for e in sds_data.enrollments if e.role == 'teacher'])}"
            )

    except FileNotFoundError as e:
        console.print(f"[red]Error: File not found: {e}[/red]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from e


@app.command()
def version() -> None:
    """Show version information."""
    table = Table(title="SDS2Roster Version Information")
    table.add_column("Item", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Version", __version__)
    table.add_row("Python", ">=3.10")
    table.add_row("License", "MIT")

    console.print(table)


@azure_app.command("upload")
def azure_upload(
    input_path: Path = typer.Argument(..., help="Path to local CSV files directory"),
    container: str = typer.Option(..., "--container", "-c", help="Azure Blob container name"),
    prefix: str = typer.Option("", "--prefix", "-p", help="Blob prefix (folder path)"),
    connection_string: Optional[str] = typer.Option(
        None, "--connection-string", help="Azure Storage connection string"
    ),
) -> None:
    """Upload CSV files to Azure Blob Storage.

    Example:
        sds2roster azure upload ./data --container sds-files --prefix input/
    """
    try:
        from sds2roster.azure.blob_storage import BlobStorageClient
    except ImportError:
        console.print(
            "[red]Error: Azure dependencies not installed. "
            "Run: pip install sds2roster[azure][/red]"
        )
        raise typer.Exit(code=1)

    # Get connection string from env if not provided
    conn_str = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        console.print(
            "[red]Error: Azure connection string not provided. "
            "Use --connection-string or set AZURE_STORAGE_CONNECTION_STRING[/red]"
        )
        raise typer.Exit(code=1)

    console.print("[bold blue]Uploading files to Azure Blob Storage[/bold blue]")
    console.print(f"Container: [cyan]{container}[/cyan]")
    console.print(f"Prefix: [cyan]{prefix or '(root)'}[/cyan]")
    console.print()

    try:
        client = BlobStorageClient(connection_string=conn_str, container_name=container)
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            task = progress.add_task("Uploading files...", total=None)
            urls = client.upload_directory(input_path, prefix=prefix)
            progress.update(task, completed=True)

        console.print(f"[green]Successfully uploaded {len(urls)} files[/green]")
        for filename, url in urls.items():
            console.print(f"  • {filename}")

    except Exception as e:
        console.print(f"[red]Error uploading files: {e}[/red]")
        raise typer.Exit(code=1) from e


@azure_app.command("download")
def azure_download(
    output_path: Path = typer.Argument(..., help="Path to download files to"),
    container: str = typer.Option(..., "--container", "-c", help="Azure Blob container name"),
    prefix: str = typer.Option("", "--prefix", "-p", help="Blob prefix filter"),
    connection_string: Optional[str] = typer.Option(
        None, "--connection-string", help="Azure Storage connection string"
    ),
) -> None:
    """Download CSV files from Azure Blob Storage.

    Example:
        sds2roster azure download ./data --container sds-files --prefix output/
    """
    try:
        from sds2roster.azure.blob_storage import BlobStorageClient
    except ImportError:
        console.print(
            "[red]Error: Azure dependencies not installed. "
            "Run: pip install sds2roster[azure][/red]"
        )
        raise typer.Exit(code=1)

    conn_str = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        console.print(
            "[red]Error: Azure connection string not provided. "
            "Use --connection-string or set AZURE_STORAGE_CONNECTION_STRING[/red]"
        )
        raise typer.Exit(code=1)

    console.print("[bold blue]Downloading files from Azure Blob Storage[/bold blue]")
    console.print(f"Container: [cyan]{container}[/cyan]")
    console.print(f"Prefix: [cyan]{prefix or '(all)'}[/cyan]")
    console.print()

    try:
        client = BlobStorageClient(connection_string=conn_str, container_name=container)
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            task = progress.add_task("Downloading files...", total=None)
            files = client.download_directory(output_path, prefix=prefix)
            progress.update(task, completed=True)

        console.print(f"[green]Successfully downloaded {len(files)} files[/green]")
        for file_path in files:
            console.print(f"  • {file_path.name}")

    except Exception as e:
        console.print(f"[red]Error downloading files: {e}[/red]")
        raise typer.Exit(code=1) from e


@azure_app.command("log")
def azure_log(
    conversion_id: str = typer.Argument(..., help="Conversion job ID"),
    source_type: str = typer.Option("SDS", "--source", "-s", help="Source data type"),
    target_type: str = typer.Option("OneRoster", "--target", "-t", help="Target data type"),
    status: str = typer.Option("success", "--status", help="Job status"),
    connection_string: Optional[str] = typer.Option(
        None, "--connection-string", help="Azure Table Storage connection string"
    ),
) -> None:
    """Log a conversion job to Azure Table Storage.

    Example:
        sds2roster azure log job-123 --status success
    """
    try:
        from sds2roster.azure.table_storage import TableStorageClient
    except ImportError:
        console.print(
            "[red]Error: Azure dependencies not installed. "
            "Run: pip install sds2roster[azure][/red]"
        )
        raise typer.Exit(code=1)

    conn_str = connection_string or os.getenv("AZURE_TABLE_CONNECTION_STRING")
    if not conn_str:
        console.print(
            "[red]Error: Azure connection string not provided. "
            "Use --connection-string or set AZURE_TABLE_CONNECTION_STRING[/red]"
        )
        raise typer.Exit(code=1)

    try:
        client = TableStorageClient(connection_string=conn_str)
        client.log_conversion(
            conversion_id=conversion_id,
            source_type=source_type,
            target_type=target_type,
            status=status,
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
        )

        console.print(f"[green]Logged conversion job: {conversion_id}[/green]")
        console.print(f"  Source: {source_type}")
        console.print(f"  Target: {target_type}")
        console.print(f"  Status: {status}")

    except Exception as e:
        console.print(f"[red]Error logging conversion: {e}[/red]")
        raise typer.Exit(code=1) from e


@azure_app.command("list-jobs")
def azure_list_jobs(
    source_type: Optional[str] = typer.Option(None, "--source", "-s", help="Filter by source type"),
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status"),
    limit: int = typer.Option(20, "--limit", "-n", help="Maximum number of jobs to list"),
    connection_string: Optional[str] = typer.Option(
        None, "--connection-string", help="Azure Table Storage connection string"
    ),
) -> None:
    """List conversion jobs from Azure Table Storage.

    Example:
        sds2roster azure list-jobs --source SDS --status success --limit 10
    """
    try:
        from sds2roster.azure.table_storage import TableStorageClient
    except ImportError:
        console.print(
            "[red]Error: Azure dependencies not installed. "
            "Run: pip install sds2roster[azure][/red]"
        )
        raise typer.Exit(code=1)

    conn_str = connection_string or os.getenv("AZURE_TABLE_CONNECTION_STRING")
    if not conn_str:
        console.print(
            "[red]Error: Azure connection string not provided. "
            "Use --connection-string or set AZURE_TABLE_CONNECTION_STRING[/red]"
        )
        raise typer.Exit(code=1)

    try:
        client = TableStorageClient(connection_string=conn_str)
        conversions = client.list_conversions(source_type=source_type, status=status, limit=limit)

        if not conversions:
            console.print("[yellow]No conversion jobs found[/yellow]")
            return

        table = Table(title="Conversion Jobs")
        table.add_column("Job ID", style="cyan")
        table.add_column("Source", style="magenta")
        table.add_column("Target", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Timestamp", style="blue")

        for conv in conversions:
            table.add_row(
                conv.get("RowKey", "N/A"),
                conv.get("SourceType", "N/A"),
                conv.get("TargetType", "N/A"),
                conv.get("Status", "N/A"),
                conv.get("Timestamp", "N/A"),
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(conversions)} jobs[/dim]")

    except Exception as e:
        console.print(f"[red]Error listing jobs: {e}[/red]")
        raise typer.Exit(code=1) from e


def main() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
