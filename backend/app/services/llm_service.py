from typing import Generator, Optional
import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

class LLMService:
    """
    Service class to interact with a HuggingFace Causal Language Model (LLM).
    Handles model/tokenizer loading, prompt construction, and streaming responses.
    """

    def __init__(self) -> None:
        """
        Initializes the LLMService:
        - Loads configuration settings.
        - Loads the tokenizer and model from HuggingFace Hub.
        - Sets the pad token if not present.
        """
        self.settings = get_settings()
        logger.info("Loading model %s", self.settings.HF_MODEL_NAME)

        # Map string dtype from config to torch dtype
        dtype_map = {
            "auto": "auto",
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }
        dtype = dtype_map.get(self.settings.TORCH_DTYPE, "auto")

        # Load tokenizer from HuggingFace
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.settings.HF_MODEL_NAME,
            use_fast=True,
            trust_remote_code=self.settings.TRUST_REMOTE_CODE
        )

        # Load model from HuggingFace with specified dtype and device map
        self.model = AutoModelForCausalLM.from_pretrained(
            self.settings.HF_MODEL_NAME,
            torch_dtype=None if dtype == "auto" else dtype,
            device_map=self.settings.DEVICE_MAP,
            offload_folder=self.settings.OFFLOAD_FOLDER,  # <-- folder to store offloaded weights
            trust_remote_code=self.settings.TRUST_REMOTE_CODE,
        )

        # Ensure the tokenizer has a pad token (required for some models)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def build_prompt(self, user_msg: str, system_prompt: Optional[str]) -> str:
        """
        Constructs the prompt for the LLM based on user and optional system prompt.

        Args:
            user_msg (str): The user's message.
            system_prompt (Optional[str]): An optional system prompt.

        Returns:
            str: The formatted prompt string.
        """
        if system_prompt:
            return f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{user_msg}\n\n[ASSISTANT]"
        return f"[USER]\n{user_msg}\n\n[ASSISTANT]"

    def stream_response(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> Generator[str, None, None]:
        """
        Streams the LLM's response token-by-token as a generator.

        Args:
            message (str): The user's message.
            system_prompt (Optional[str]): Optional system prompt.
            max_new_tokens (Optional[int]): Max tokens to generate.
            temperature (Optional[float]): Sampling temperature.
            top_p (Optional[float]): Nucleus sampling parameter.

        Yields:
            str: The next chunk of generated text.
        """
        s = self.settings
        # Build the full prompt for the model
        prompt = self.build_prompt(message, system_prompt)
        # Tokenize the prompt and move tensors to the model's device (CPU/GPU)
        inputs = self.tokenizer([prompt], return_tensors="pt").to(self.model.device)

        # Generation parameters, with fallbacks to config defaults
        gen_kwargs = {
            "max_new_tokens": max_new_tokens or s.MAX_NEW_TOKENS,
            "temperature": temperature if temperature is not None else s.TEMPERATURE,
            "top_p": top_p if top_p is not None else s.TOP_P,
            "do_sample": True,
            "eos_token_id": self.tokenizer.eos_token_id,
            "pad_token_id": self.tokenizer.pad_token_id,
        }

        # Set up a streamer to yield generated text as it becomes available
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )
        gen_kwargs["streamer"] = streamer

        # Run model.generate in a separate thread to avoid blocking
        thread = Thread(target=self.model.generate, kwargs={**inputs, **gen_kwargs})
        thread.start()

        # Yield new text chunks as they are produced by the streamer
        for new_text in streamer:
            yield new_text