import re
import unicodedata
from urllib.parse import urlparse, unquote


def clean_text(value: str | None) -> str:
	"""Normaliza espaços e remove quebras desnecessárias."""
	if not value:
		return ""
	return re.sub(r"\s+", " ", value).strip()


def remove_accents(value: str) -> str:
	"""Remove acentos mantendo texto legível."""
	normalized = unicodedata.normalize("NFKD", value)
	return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def slugify(value: str) -> str:
	"""Gera slug simples sem depender de biblioteca externa."""
	value = remove_accents(clean_text(value).lower())
	value = re.sub(r"[^a-z0-9]+", "-", value)
	return value.strip("-")


def extract_team_slug_from_url(url: str | None) -> str:
	"""Extrai o slug da URL /equipes/{slug}/."""
	if not url:
		return ""

	path = urlparse(url).path.strip("/")
	parts = path.split("/")

	if "equipes" in parts:
		idx = parts.index("equipes")
		if idx + 1 < len(parts):
			return unquote(parts[idx + 1].strip("/"))

	return ""


def title_from_slug(slug: str) -> str:
	"""Transforma um slug em nome legível."""
	if not slug:
		return ""
	return clean_text(slug.replace("-", " ").title())


def image_key(url: str | None) -> str:
	"""Cria chave comparável para imagens do WordPress."""
	if not url:
		return ""

	path = unquote(urlparse(url).path)
	filename = path.rsplit("/", 1)[-1].lower()

	# Remove sufixos tipo -150x150 antes da extensão.
	filename = re.sub(r"-\d+x\d+(?=\.[a-z0-9]+$)", "", filename)

	return filename

def extract_player_slug_from_url(url: str | None) -> str:
	"""Extrai slug normalizado da URL /atletas/{slug}/."""
	if not url:
		return ""

	path = urlparse(url).path.strip("/")
	parts = path.split("/")

	if "atletas" in parts:
		idx = parts.index("atletas")
		if idx + 1 < len(parts):
			return slugify(unquote(parts[idx + 1].strip("/")))

	return ""


def identity_key(value: str | None) -> str:
	"""Chave textual para comparar nomes ignorando acento, espaço e caixa."""
	if not value:
		return ""

	value = remove_accents(clean_text(value).lower())
	return "".join(ch for ch in value if ch.isalnum())