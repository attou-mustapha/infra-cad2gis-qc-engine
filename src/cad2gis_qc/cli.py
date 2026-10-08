"""CAD2GIS Quality Control CLI."""

import time
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from .ingest import load_vector_dataset
from .topology import TopologyValidator
from .reporter import export_geojson_anomalies, export_html_report
from .models import QCReportSummary

app = typer.Typer(help="CAD2GIS Quality Control & Topology Validation CLI")
console = Console()


@app.command()
def validate(
    input_file: Path = typer.Argument(..., help="Path to input vector/CAD file (GeoJSON, SHP, DXF, GPKG)"),
    output_dir: Path = typer.Option(Path("reports"), "--output-dir", "-o", help="Output directory for reports"),
    tolerance: float = typer.Option(0.5, "--tolerance", "-t", help="Topological snap tolerance in meters"),
    crs: str = typer.Option("EPSG:32188", "--crs", help="Projected metric coordinate reference system")
):
    """
    Ingests a CAD or GIS vector file, evaluates topological integrity, and generates QC reports.
    """
    start_time = time.time()
    console.print(f"[bold cyan]🔍 Ingesting {input_file}...[/bold cyan]")

    try:
        gdf = load_vector_dataset(input_file, target_crs=crs)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to load dataset: {e}[/bold red]")
        raise typer.Exit(code=1)

    total_count = len(gdf)
    console.print(f"Loaded [green]{total_count}[/green] features in CRS [yellow]{crs}[/yellow].")

    console.print(f"[bold cyan]⚙️ Running topological rules (tolerance: {tolerance}m)...[/bold cyan]")
    validator = TopologyValidator(tolerance_meters=tolerance)
    anomalies = validator.validate_linear_network(gdf)

    elapsed = time.time() - start_time
    invalid_count = len(anomalies)
    valid_count = max(0, total_count - invalid_count)
    score = max(0.0, 100.0 * (1.0 - (invalid_count / max(1, total_count))))

    # Summary table
    table = Table(title="Topological QC Inspection Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Total Features", str(total_count))
    table.add_row("Valid Features", str(valid_count))
    table.add_row("Defects Detected", str(invalid_count))
    table.add_row("Quality Score", f"{score:.1f}%")
    table.add_row("Execution Time", f"{elapsed:.2f}s")
    console.print(table)

    summary = QCReportSummary(
        file_path=str(input_file),
        total_features=total_count,
        valid_features=valid_count,
        invalid_features=invalid_count,
        quality_score=score,
        anomalies_by_type={},
        anomalies_by_severity={},
        execution_time_seconds=elapsed,
        anomalies=anomalies
    )

    # Export
    geojson_out = output_dir / f"{input_file.stem}_qc_anomalies.geojson"
    html_out = output_dir / f"{input_file.stem}_qc_report.html"

    export_geojson_anomalies(anomalies, geojson_out)
    export_html_report(summary, html_out)

    console.print(f"[bold green]✅ Inspection complete![/bold green]")
    console.print(f"📄 HTML Report: [underline]{html_out}[/underline]")
    console.print(f"🗺️ GeoJSON Defects: [underline]{geojson_out}[/underline]")


if __name__ == "__main__":
    app()
