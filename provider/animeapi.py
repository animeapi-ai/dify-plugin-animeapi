from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.client import AnimeAPIError, check_key


class AnimeAPIProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = str(credentials.get("api_key") or "").strip()
        if not api_key.startswith("ank_"):
            raise ToolProviderCredentialValidationError(
                "AnimeAPI keys start with ank_. Create one at https://animeapi.ai/dashboard/api-keys."
            )
        try:
            # Checks the key only: nothing is generated.
            check_key(api_key)
        except AnimeAPIError as e:
            raise ToolProviderCredentialValidationError(str(e)) from e
