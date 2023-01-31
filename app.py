import os
import torch
from diffusers import (StableDiffusionPipeline,
                       PNDMScheduler, LMSDiscreteScheduler, DDIMScheduler, EulerDiscreteScheduler,
                       EulerAncestralDiscreteScheduler, DPMSolverMultistepScheduler)
import torch
from torch import autocast
import base64
from io import BytesIO
from PIL import Image

model_path = "runwayml/stable-diffusion-v1-5"


def make_scheduler(name, config):
    return {
        'PNDM': PNDMScheduler.from_config(config),
        'KLMS': LMSDiscreteScheduler.from_config(config),
        'DDIM': DDIMScheduler.from_config(config),
        'K_EULER': EulerDiscreteScheduler.from_config(config),
        'K_EULER_ANCESTRAL': EulerAncestralDiscreteScheduler.from_config(config),
        'DPMSolverMultistep': DPMSolverMultistepScheduler.from_config(config),
    }[name]


def init():
    global model
    HF_AUTH_TOKEN = os.getenv('HF_AUTH_TOKEN')
    model = StableDiffusionPipeline.from_pretrained(model_path,
                                                    torch_dtype=torch.float16, use_auth_token=HF_AUTH_TOKEN)


def inference(model_inputs):
    global model

    prompt = model_inputs.get('prompt', None)
    negative_prompt = model_inputs.get('negative_prompt', None)
    height = model_inputs.get('height', 512)
    width = model_inputs.get('width', 512)
    steps = model_inputs.get('steps', 20)
    guidance_scale = model_inputs.get('guidance_scale', 7)
    seed = model_inputs.get('seed', None)
    scheduler = model_inputs.get('scheduler', 'K_EULER_ANCESTRAL')

    extra_kwargs = {}
    if not prompt:
        return {'message': 'No prompt was provided'}

    extra_kwargs = {
        "width": width,
        "height": height,
    }

    model = model.to("cuda")

    generator = None
    if seed:
        generator = torch.Generator('cuda').manual_seed(seed)
    model.scheduler = make_scheduler(scheduler, model.scheduler.config)
    with autocast('cuda'):
        image = model(
            prompt,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            generator=generator,
            num_inference_steps=steps,
            **extra_kwargs,
        ).images[0]

    buffered = BytesIO()
    image.save(buffered, format='JPEG')
    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return {'image_base64': image_base64}
