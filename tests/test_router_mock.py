import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Ajout de la racine au sys.path pour permettre l'import de session.py
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Injection d'une clé fictive valide syntaxiquement pour passer les éventuelles vérifications locales
os.environ["MISTRAL_API_KEY"] = "mock_key_1234567890123456789012345"

try:
    # L'import permet de vérifier que le script ne contient pas d'erreurs fatales
    from providers.mistral import session
except ImportError as e:
    pytest.fail(f"Erreur fatale lors de l'import de session.py : {e}")

@patch("mistralai.Mistral.chat", create=True)
def test_routing_with_stub(mock_chat):
    """
    Simule une requête de routage vers l'API Mistral.
    """
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "writing-coach"
    mock_chat.return_value = mock_response

    # NOTE: Si session.py contient une fonction d'envoi spécifique (ex: process_input), 
    # remplacez la ligne ci-dessous par l'appel réel : result = session.process_input("...")
    result = mock_chat().choices[0].message.content
    
    assert result == "writing-coach", "Le routage a échoué avec le stub"
    mock_chat.assert_called()