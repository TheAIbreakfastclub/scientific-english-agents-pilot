import pytest
from pathlib import Path

def get_project_root():
    return Path(__file__).parent.parent

def test_markdown_agents_exist_and_readable():
    """
    Vérifie que tous les agents déclarés ont bien leur fichier d'instructions (agent.md)
    et qu'ils sont lisibles par le système (crucial pour le routage de l'IA).
    """
    root = get_project_root()
    agents = [
        "assessment",
        "communication-coach",
        "critical-reviewer",
        "language-tutor",
        "lexical-expert",
        "writing-coach"
    ]

    for agent in agents:
        agent_path = root / "src" / "agents" / agent / "agent.md"
        assert agent_path.exists(), f"Fichier système manquant pour l'agent {agent} : {agent_path}"

        with open(agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 100, f"Le fichier {agent_path} semble vide. Risque de Prompt Drift."

def test_assessment_rubrics_integrity():
    """
    Vérifie que l'agent d'évaluation a accès à ses grilles de correction.
    """
    root = get_project_root()
    rubrics_dir = root / "src" / "agents" / "assessment" / "rubrics"
    
    assert rubrics_dir.exists(), "Le dossier des grilles d'évaluation (rubrics) a disparu."
    
    required_rubrics = ["abstract.md", "imrad.md", "oral.md"]
    for rubric in required_rubrics:
        rubric_path = rubrics_dir / rubric
        assert rubric_path.exists(), f"Grille d'évaluation manquante : {rubric}"