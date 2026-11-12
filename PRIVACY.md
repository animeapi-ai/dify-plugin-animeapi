# Privacy

This plugin sends data to one service only: AnimeAPI (`https://animeapi.ai`).

## What is sent

- **Your AnimeAPI key**, in the `Authorization` header of each request, to identify your account.
- **The prompt and options** you (or your model) give the tool: the text description, model, orientation and the enhance setting.

Nothing else from your Dify workspace is sent: no conversation history, user identifiers, files or other variables.

## What comes back

The generated image, the tags the model received, the price and your remaining balance. The plugin downloads the image from `animeapi.ai` and hands it to Dify, which stores it under your workspace's own file settings.

## What the plugin stores

Nothing. The plugin keeps no data, writes no files and has no logging of prompts or keys. Your key is stored by Dify as an encrypted credential.

## What AnimeAPI keeps

AnimeAPI records each request against your account (prompt, model, status and cost) for billing, support and abuse prevention, as described in its privacy policy: https://animeapi.ai/privacy. Terms and acceptable use: https://animeapi.ai/terms.

## Contact

contact@animeapi.ai
