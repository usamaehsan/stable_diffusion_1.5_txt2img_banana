import torch
from diffusers import StableDiffusionPipeline
import os

model_path = "runwayml/stable-diffusion-v1-5"
inpainting_model_path = "runwayml/stable-diffusion-inpainting"


def download_model():
    HF_AUTH_TOKEN = os.getenv("HF_AUTH_TOKEN")
    txt2img_pipe = StableDiffusionPipeline.from_pretrained(model_path,
                                                           torch_dtype=torch.float16, use_auth_token=HF_AUTH_TOKEN)


if __name__ == "__main__":
    download_model()
