import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

TEMPLATE_SCHEMA_FIELDS = [
    "name",
    "assistant_role",
    "required_fields",
    "task_description",
    "output_format",
    "constraints_default",
]


class TemplateService:
    def __init__(self, templates_dir: str = "storage/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, dict] = {}

    def _load_file(self, path: Path) -> Optional[dict]:
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Erro ao carregar template {path.name}: {e}")
            return None

    def load_all(self) -> List[Dict]:
        templates = []
        for fpath in sorted(self.templates_dir.glob("*.json")):
            data = self._load_file(fpath)
            if data and self.validate_schema(data):
                self._cache[data["name"]] = data
                templates.append(data)
        return templates

    def get(self, name: str) -> Optional[Dict]:
        if name in self._cache:
            return self._cache[name]

        fpath = self.templates_dir / f"{name}.json"
        if not fpath.exists():
            for fpath in self.templates_dir.glob("*.json"):
                data = self._load_file(fpath)
                if data and data.get("name") == name:
                    self._cache[name] = data
                    return data
            return None

        data = self._load_file(fpath)
        if data and self.validate_schema(data):
            self._cache[name] = data
        return data

    def save(self, template: Dict) -> bool:
        if not self.validate_schema(template):
            logger.error(f"Template invalido: campos obrigatorios ausentes")
            return False

        fpath = self.templates_dir / f"{template['name']}.json"
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            self._cache[template["name"]] = template
            return True
        except OSError as e:
            logger.error(f"Erro ao salvar template: {e}")
            return False

    def validate_schema(self, template: Dict) -> bool:
        return all(field in template for field in TEMPLATE_SCHEMA_FIELDS)

    def list_names(self) -> List[str]:
        return [t["name"] for t in self.load_all()]
