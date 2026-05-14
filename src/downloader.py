"""
Generic HTTP downloader with retry logic and progress reporting.
"""
import time
from typing import Optional
import requests
from tqdm import tqdm


class DownloadError(Exception):
    """Raised when a download fails after all retries."""
    def __init__(self, url: str, attempts: int, last_error: Exception):
        self.url = url
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"Download failed after {attempts} attempts: {url} — {last_error}")


class Downloader:
    """Generic HTTP downloader with retry, progress bar, and timeout."""

    def __init__(self, max_retries: int = 3, timeout: int = 30,
                 chunk_size: int = 8192, show_progress: bool = True):
        self.max_retries = max_retries
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.show_progress = show_progress

    def _should_retry(self, error: Exception, attempt: int) -> bool:
        if attempt >= self.max_retries:
            return False
        if isinstance(error, (requests.ConnectionError, requests.Timeout)):
            return True
        if isinstance(error, requests.HTTPError):
            status = error.response.status_code if hasattr(error, 'response') else 0
            return status >= 500
        return False

    def download(self, url: str, output_path: str,
                 headers: Optional[dict] = None,
                 params: Optional[dict] = None) -> str:
        """
        Download a file from url to output_path.

        Returns the local file path on success.
        Raises DownloadError after exhausting retries.
        """
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(
                    url, headers=headers, params=params,
                    timeout=self.timeout, stream=True
                )
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))

                with open(output_path, 'wb') as f:
                    if self.show_progress and total_size > 0:
                        with tqdm(total=total_size, unit='B', unit_scale=True,
                                  desc=output_path.split('/')[-1][:30]) as pbar:
                            for chunk in response.iter_content(chunk_size=self.chunk_size):
                                f.write(chunk)
                                pbar.update(len(chunk))
                    else:
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            f.write(chunk)

                return output_path

            except (requests.ConnectionError, requests.Timeout) as e:
                last_error = e
                if attempt < self.max_retries:
                    wait = 2 ** (attempt - 1)
                    time.sleep(wait)
            except requests.HTTPError as e:
                status = e.response.status_code if hasattr(e, 'response') else 0
                if status >= 500 and attempt < self.max_retries:
                    last_error = e
                    wait = 2 ** (attempt - 1)
                    time.sleep(wait)
                else:
                    raise DownloadError(url, attempt, e)

        raise DownloadError(url, self.max_retries, last_error)

    def download_json(self, url: str, params: Optional[dict] = None,
                      headers: Optional[dict] = None) -> dict:
        """Download and parse JSON response."""
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(
                    url, headers=headers, params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except (requests.ConnectionError, requests.Timeout) as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(2 ** (attempt - 1))
            except requests.HTTPError as e:
                status = e.response.status_code if hasattr(e, 'response') else 0
                if status >= 500 and attempt < self.max_retries:
                    last_error = e
                    time.sleep(2 ** (attempt - 1))
                else:
                    raise DownloadError(url, attempt, e)
            except ValueError as e:
                raise DownloadError(url, attempt, e)

        raise DownloadError(url, self.max_retries, last_error)
