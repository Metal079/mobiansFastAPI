import io
import base64
import logging
import random

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin


# ---- image manipulation -----

# Create the watermark image and font objects outside the function
#watermark_text = "Mobians.ai"
opacity = 128
font_file_path = r"fonts/Roboto-Medium.ttf"
font = ImageFont.truetype(font_file_path, 25)


# async def remove_alpha_channel(image):
#     # Convert image to RGB if it has an alpha channel
#     if image.mode == "RGBA":
#         buffer = io.BytesIO()
#         # Separate alpha channel and add white background
#         background = Image.new("RGBA", image.size, (255, 255, 255))
#         alpha_composite = Image.alpha_composite(background, image).convert("RGB")
#         alpha_composite.save(buffer, format="PNG")
#         return alpha_composite
#     else:
#         return image


async def add_image_metadata(image, request_data):
    img_io = io.BytesIO()
    image_with_watermark = await add_watermark(image)

    metadata = PngImagePlugin.PngInfo()
    metadata_dict = {
        "model": "Mobians.ai / SonicDiffusionV4",
        "Disclaimer": "The image is generated by Mobians.ai. The image is not real and is generated by an AI.",
    }

    try:
        if request_data.job_type != "txt2img":
            metadata_dict["NOTE"] = (
                "The image was not generated purely using txt2img, using the info below may not give you the same results."
            )

        metadata_dict["prompt"] = request_data.prompt
        request_data.negative_prompt = request_data.negative_prompt.replace("admin", "")
        metadata_dict["negative_prompt"] = request_data.negative_prompt
        metadata_dict["seed"] = str(request_data.seed)
        metadata_dict["cfg"] = str(request_data.guidance_scale)
        metadata_dict["job_type"] = request_data.job_type
    except Exception as e:
        logging.error(f"Error adding metadata to image: {e}")
        with open("error_log.txt", "a") as f:
            f.write(f"Error adding metadata to image: {request_data}\n")

    for key, value in metadata_dict.items():
        metadata.add_text(key, value)

    image_with_watermark.save(img_io, format="PNG", pnginfo=metadata)
    img_io.seek(0)
    base64_image = base64.b64encode(img_io.getvalue()).decode("utf-8")
    return base64_image


async def add_watermark(image):
    # randomly pick between EggmanEmpire.ai or Plumbers.ai
    options = ["JSMetal.com", "EggmanEmpire.ai", "tweetrdot.com", "y.com", "/r/SonicTheHedgehog", "Plumbers.ai", "Moon says he loves you", "Mobian.pie", "01001100"]
    watermark_text = random.choice(options)

    watermark = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)

    stroke_width = 2
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            draw.text(
                (10 + dx, 10 + dy), watermark_text, font=font, fill=(0, 0, 0, opacity)
            )

    draw.text((10, 10), watermark_text, font=font, fill=(255, 255, 255, opacity))

    image_with_watermark = Image.alpha_composite(image.convert("RGBA"), watermark)
    return image_with_watermark
