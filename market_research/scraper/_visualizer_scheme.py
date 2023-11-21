from pathlib import Path

class Visualizer:
    def __init__(self, output_folder_path="results"):
        self.output_folder = None
        self._set_output_path(output_folder_path=output_folder_path)


    def _set_output_path(self, output_folder_path="results"):
        if output_folder_path is not None:
            self.output_folder = Path(output_folder_path)
            if not self.output_folder.exists():
                self.output_folder.mkdir(parents=True, exist_ok=True)
