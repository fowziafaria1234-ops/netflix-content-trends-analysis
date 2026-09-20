"""Run the full pipeline: clean -> metrics -> charts -> dashboard."""
from build_dashboard import main as dashboard
from build_metrics import main as metrics
from clean_transform import main as clean
from create_visuals import main as visuals

if __name__ == "__main__":
    clean(); metrics(); visuals(); dashboard(); print("Pipeline completed successfully.")
