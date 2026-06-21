import random
import time

import requests


DEFAULT_HEADERS = {
	"User-Agent": (
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
		"AppleWebKit/537.36 (KHTML, like Gecko) "
		"Chrome/120.0 Safari/537.36"
	),
	"Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


class HttpClient:
	"""Cliente HTTP com retry, timeout e delay leve."""

	def __init__(
		self,
		timeout: int = 25,
		retries: int = 3,
		min_delay: float = 0.8,
		max_delay: float = 2.0,
	) -> None:
		self.timeout = timeout
		self.retries = retries
		self.min_delay = min_delay
		self.max_delay = max_delay
		self.session = requests.Session()
		self.session.headers.update(DEFAULT_HEADERS)

	def get_text(self, url: str) -> str:
		"""Baixa HTML com retry simples."""
		last_error: Exception | None = None

		for attempt in range(1, self.retries + 1):
			try:
				response = self.session.get(url, timeout=self.timeout)
				response.raise_for_status()

				self._polite_sleep()
				return response.content.decode("utf-8", errors="replace")

			except requests.RequestException as exc:
				last_error = exc
				wait = min(2 * attempt, 8) + random.uniform(0, 1)
				time.sleep(wait)

		raise RuntimeError(f"Falha ao baixar URL após retries: {url}") from last_error

	def _polite_sleep(self) -> None:
		"""Evita rajadas agressivas no site."""
		time.sleep(random.uniform(self.min_delay, self.max_delay))